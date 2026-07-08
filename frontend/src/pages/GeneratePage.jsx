import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  ArrowLeft, Sparkles, Loader2, FileText, Layout, Palette,
  Users, MessageSquare, Sliders, Play, CheckCircle2
} from 'lucide-react'
import useStore from '../store/useStore'
import { api, streamGenerate } from '../services/api'

const STYLE_OPTIONS = [
  { value: 'style-b', label: '瑞士国际主义', icon: Layout, desc: '16列网格 · 直角 · 高饱和锚点色' },
  { value: 'style-a', label: '电子杂志 × 电子墨水', icon: Palette, desc: 'Monocle风 · 衬线 · 大片留白' },
]

const STYLE_THEMES = {
  'style-a': [
    { value: 'ink-classic', label: '墨水经典', preview: '#c41e3a' },
    { value: 'indigo-porcelain', label: '靛蓝瓷', preview: '#3b5998' },
    { value: 'forest-ink', label: '森林墨', preview: '#4a7c59' },
    { value: 'kraft-paper', label: '牛皮纸', preview: '#c4732e' },
    { value: 'sand-dune', label: '沙丘', preview: '#c4945a' },
  ],
  'style-b': [
    { value: 'ikb-blue', label: 'IKB 克莱因蓝', preview: '#0015ff' },
    { value: 'lemon-yellow', label: '柠檬黄', preview: '#ffe600' },
    { value: 'lemon-green', label: '柠檬绿', preview: '#00ff62' },
    { value: 'safety-orange', label: '安全橙', preview: '#ff5f00' },
  ],
}

const TONE_OPTIONS = [
  { value: '', label: '自动判断' },
  { value: 'professional', label: '专业严谨' },
  { value: 'casual', label: '轻松活泼' },
  { value: 'academic', label: '学术研究' },
  { value: 'inspirational', label: '激励人心' },
  { value: 'minimal', label: '极简风格' },
]

const SLIDE_COUNT_OPTIONS = [5, 8, 10, 12, 15, 20, 25]

/** Safely convert an error to a string message. */
function errMsg(err) {
  if (!err) return '未知错误'
  if (typeof err === 'string') return err
  if (err.message) return err.message
  if (err.detail) return err.detail
  try { return JSON.stringify(err) } catch { return String(err) }
}

export default function GeneratePage() {
  const navigate = useNavigate()
  const topic = useStore((s) => s.topic)
  const style = useStore((s) => s.style)
  const theme = useStore((s) => s.theme)
  const audience = useStore((s) => s.audience)
  const slideCount = useStore((s) => s.slideCount)
  const language = useStore((s) => s.language)
  const tone = useStore((s) => s.tone)
  const additionalRequirements = useStore((s) => s.additionalRequirements)
  const includeImages = useStore((s) => s.includeImages)
  const bgType = useStore((s) => s.bgType)
  const loading = useStore((s) => s.loading)
  const streamMessages = useStore((s) => s.streamMessages)
  const outline = useStore((s) => s.outline)
  const error = useStore((s) => s.error)
  const setField = useStore((s) => s.setField)
  const setOutline = useStore((s) => s.setOutline)
  const setLoading = useStore((s) => s.setLoading)
  const setError = useStore((s) => s.setError)
  const setStep = useStore((s) => s.setStep)
  const addStreamMessage = useStore((s) => s.addStreamMessage)
  const clearStreamMessages = useStore((s) => s.clearStreamMessages)
  const resetStore = useStore((s) => s.reset)

  const [showAdvanced, setShowAdvanced] = useState(false)

  const handleGenerate = async () => {
    if (!topic.trim()) return

    setLoading(true)
    setError(null)
    clearStreamMessages()

    const data = {
      topic: topic.trim(),
      style,
      theme,
      audience: audience.trim() || null,
      slide_count: slideCount,
      language,
      tone: tone || null,
      additional_requirements: additionalRequirements.trim() || null,
      include_images: includeImages,
    }

    // Try streaming first, fall back to non-streaming on error
    streamGenerate(data, {
      onProgress: (msg) => {
        addStreamMessage(msg)
        if (msg.outline) {
          setOutline(msg.outline)
        }
      },
      onComplete: () => {
        setLoading(false)
        setStep('outline')
      },
      onError: (err) => {
        console.warn('Stream failed, falling back to non-streaming:', errMsg(err))
        generateNonStream(data)
      },
    })
  }

  const generateNonStream = async (data) => {
    try {
      addStreamMessage({ step: 'generating', message: '正在生成PPT大纲...' })
      const result = await api.generateFull(data)
      setOutline(result)
      setLoading(false)
      setStep('outline')
    } catch (err) {
      setError(errMsg(err))
      setLoading(false)
    }
  }

  const handleViewPreview = () => {
    navigate('/preview')
  }

  const currentThemes = STYLE_THEMES[style] || STYLE_THEMES['style-b']

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-950/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <button onClick={() => navigate('/')} className="btn-icon flex items-center gap-2">
            <ArrowLeft size={18} /> 返回
          </button>
          <h1 className="text-lg font-semibold">创建 PPT</h1>
          <div className="w-20" />
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-10">
        {/* Style Selector */}
        <section className="mb-8 animate-fade-in-up">
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">选择风格</h2>
          <div className="grid grid-cols-2 gap-4">
            {STYLE_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                onClick={() => {
                  setField('style', opt.value)
                  setField('theme', opt.value === 'style-a' ? 'ink-classic' : 'ikb-blue')
                }}
                className={`card text-left p-5 transition-all duration-200 ${
                  style === opt.value
                    ? 'border-blue-500/50 bg-blue-500/5 ring-1 ring-blue-500/30'
                    : 'hover:border-gray-700'
                }`}
              >
                <div className="flex items-center gap-3 mb-2">
                  <opt.icon size={20} className={style === opt.value ? 'text-blue-400' : 'text-gray-500'} />
                  <span className="font-semibold">{opt.label}</span>
                  {style === opt.value && <CheckCircle2 size={16} className="text-blue-400 ml-auto" />}
                </div>
                <p className="text-xs text-gray-500">{opt.desc}</p>
              </button>
            ))}
          </div>
        </section>

        {/* Theme Selector */}
        <section className="mb-8 animate-fade-in-up" style={{ animationDelay: '0.05s' }}>
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">配色主题</h2>
          <div className="flex gap-3 flex-wrap">
            {currentThemes.map((t) => (
              <button
                key={t.value}
                onClick={() => setField('theme', t.value)}
                className={`flex items-center gap-2 px-4 py-3 rounded-lg border transition-all ${
                  theme === t.value
                    ? 'border-white/30 bg-gray-800 ring-1 ring-white/20'
                    : 'border-gray-800 bg-gray-900 hover:border-gray-700'
                }`}
              >
                <span className="w-4 h-4 rounded-full border border-white/20" style={{ backgroundColor: t.preview }} />
                <span className="text-sm">{t.label}</span>
              </button>
            ))}
          </div>
        </section>

        {/* Topic Input */}
        <section className="mb-8 animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">PPT 主题</h2>
          <textarea
            value={topic}
            onChange={(e) => setField('topic', e.target.value)}
            placeholder="输入你的PPT主题，例如：2024年AI行业发展趋势分析、我们产品的年度总结与展望..."
            className="input-field h-32 resize-none"
            disabled={loading}
          />
          <p className="text-xs text-gray-600 mt-2">
            提示：主题越具体，生成的内容越精准。可以包含行业、受众、目的等信息。
          </p>
        </section>

        {/* Basic Options */}
        <section className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6 animate-fade-in-up" style={{ animationDelay: '0.15s' }}>
          <div>
            <label className="text-xs text-gray-500 mb-1.5 block">目标受众</label>
            <input
              type="text"
              value={audience}
              onChange={(e) => setField('audience', e.target.value)}
              placeholder="如：投资人、技术团队"
              className="input-field text-sm py-2.5"
              disabled={loading}
            />
          </div>
          <div>
            <label className="text-xs text-gray-500 mb-1.5 block">页数</label>
            <select
              value={slideCount}
              onChange={(e) => setField('slideCount', parseInt(e.target.value))}
              className="input-field text-sm py-2.5"
              disabled={loading}
            >
              {SLIDE_COUNT_OPTIONS.map((n) => (
                <option key={n} value={n}>{n} 页</option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-xs text-gray-500 mb-1.5 block">语言风格</label>
            <select
              value={tone}
              onChange={(e) => setField('tone', e.target.value)}
              className="input-field text-sm py-2.5"
              disabled={loading}
            >
              {TONE_OPTIONS.map((t) => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-xs text-gray-500 mb-1.5 block">语言</label>
            <select
              value={language}
              onChange={(e) => setField('language', e.target.value)}
              className="input-field text-sm py-2.5"
              disabled={loading}
            >
              <option value="zh-CN">中文</option>
              <option value="en">English</option>
            </select>
          </div>
        </section>

        {/* Advanced Options Toggle */}
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-300 mb-4 transition-colors"
        >
          <Sliders size={14} />
          {showAdvanced ? '收起高级选项' : '展开高级选项'}
        </button>

        {showAdvanced && (
          <section className="mb-8 animate-fade-in-up">
            <div className="card space-y-4">
              <div>
                <label className="text-sm text-gray-400 mb-2 block">额外要求</label>
                <textarea
                  value={additionalRequirements}
                  onChange={(e) => setField('additionalRequirements', e.target.value)}
                  placeholder="例如：每页不超过50字、多用数据图表、包含SWOT分析..."
                  className="input-field h-24 resize-none text-sm"
                  disabled={loading}
                />
              </div>
              <div className="space-y-3">
                <div>
                  <label className="text-sm text-gray-400 mb-2 block">幻灯片背景类型</label>
                  <div className="flex gap-2 flex-wrap">
                    {[
                      { value: 'gradient', label: '🎨 渐变', desc: '内容匹配的CSS渐变' },
                      { value: 'photo', label: '📸 摄影', desc: '关键词主题照片' },
                      { value: 'pattern', label: '🔷 几何', desc: 'SVG几何图案纹理' },
                      { value: 'none', label: '⬜ 无背景', desc: '保持默认简洁风格' },
                    ].map((opt) => (
                      <button
                        key={opt.value}
                        onClick={() => setField('bgType', opt.value)}
                        disabled={loading}
                        className={`flex flex-col items-start gap-0.5 px-3 py-2 rounded-lg border text-left transition-all ${
                          bgType === opt.value
                            ? 'border-purple-500/50 bg-purple-500/10 ring-1 ring-purple-500/30'
                            : 'border-gray-800 bg-gray-900 hover:border-gray-700'
                        }`}
                      >
                        <span className="text-sm font-medium">{opt.label}</span>
                        <span className="text-[10px] text-gray-500">{opt.desc}</span>
                      </button>
                    ))}
                  </div>
                </div>
                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={includeImages}
                    onChange={(e) => setField('includeImages', e.target.checked)}
                    className="w-4 h-4 rounded border-gray-600 bg-gray-800 text-blue-600 focus:ring-blue-500"
                    disabled={loading}
                  />
                  <div>
                    <span className="text-sm text-gray-300">自动生成配图</span>
                    <p className="text-xs text-gray-500 mt-0.5">使用高质量占位图片填充全屏图、左右图布局</p>
                  </div>
                </label>
              </div>
            </div>
          </section>
        )}

        {/* Generate Button */}
        <div className="flex items-center gap-4 mb-8">
          <button
            onClick={handleGenerate}
            disabled={!topic.trim() || loading}
            className="btn-primary flex items-center gap-3 text-lg px-10 py-4"
          >
            {loading ? (
              <>
                <Loader2 size={22} className="animate-spin" />
                生成中...
              </>
            ) : (
              <>
                <Sparkles size={22} />
                开始生成 PPT
              </>
            )}
          </button>
          {loading && (
            <button onClick={() => window.location.reload()} className="btn-secondary text-sm">
              取消
            </button>
          )}
        </div>

        {/* Error */}
        {error && (
          <div className="card border-red-500/30 bg-red-500/5 mb-8">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}

        {/* Stream Progress */}
        {streamMessages.length > 0 && (
          <div className="card mb-8 animate-fade-in-up">
            <h3 className="text-sm font-semibold text-gray-400 mb-4">生成进度</h3>
            <div className="space-y-3 max-h-64 overflow-y-auto">
              {streamMessages.map((msg, i) => (
                <div key={i} className="flex items-start gap-3 text-sm">
                  {msg.step === 'done' ? (
                    <CheckCircle2 size={16} className="text-green-400 mt-0.5 shrink-0" />
                  ) : msg.step === 'error' ? (
                    <span className="text-red-400 mt-0.5 shrink-0">✕</span>
                  ) : (
                    <Loader2 size={14} className="animate-spin text-blue-400 mt-0.5 shrink-0" />
                  )}
                  <span className="text-gray-300">{msg.message}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Result: Outline */}
        {outline && !loading && (
          <section className="animate-fade-in-up">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">{outline.title}</h2>
              <button onClick={handleViewPreview} className="btn-primary flex items-center gap-2">
                <Play size={18} /> 预览 PPT
              </button>
            </div>
            {outline.subtitle && (
              <p className="text-gray-400 mb-6">{outline.subtitle}</p>
            )}

            <div className="space-y-2">
              {outline.slides.map((slide, i) => (
                <SlideCard key={i} slide={slide} index={i} />
              ))}
            </div>

            <div className="flex items-center gap-3 mt-6">
              <button onClick={handleViewPreview} className="btn-primary flex items-center gap-2">
                <Play size={18} /> 预览 HTML 演示
              </button>
              <button onClick={() => { setField('topic', ''); resetStore(); }} className="btn-secondary">
                重新生成
              </button>
            </div>
          </section>
        )}
      </main>
    </div>
  )
}

function SlideCard({ slide, index }) {
  const [expanded, setExpanded] = useState(false)
  const colorMap = {
    cover: 'border-l-blue-500',
    section: 'border-l-purple-500',
    closing: 'border-l-gray-500',
    quote: 'border-l-yellow-500',
    'big-number': 'border-l-orange-500',
    'image-full': 'border-l-pink-500',
    'image-left': 'border-l-cyan-500',
    'image-right': 'border-l-cyan-500',
  }
  const borderColor = colorMap[slide.layout] || 'border-l-green-500'
  const isImage = slide.layout && ['image-full', 'image-left', 'image-right'].includes(slide.layout)

  return (
    <div className={`card border-l-2 ${borderColor} p-4 cursor-pointer hover:bg-gray-800/50 transition-colors`}
         onClick={() => setExpanded(!expanded)}>
      <div className="flex items-center gap-3">
        <span className="text-xs text-gray-600 w-8 shrink-0">#{index + 1}</span>
        <span className={`text-xs px-1.5 py-0.5 rounded uppercase shrink-0 ${isImage ? 'bg-pink-500/20 text-pink-400' : 'bg-gray-800 text-gray-500'}`}>
          {slide.layout}
        </span>
        <span className="text-sm font-medium truncate">{slide.title || '（无标题）'}</span>
        {isImage && <span className="text-xs text-pink-400">🖼</span>}
        {slide.bullet_points && (
          <span className="text-xs text-gray-600">{slide.bullet_points.length} 要点</span>
        )}
      </div>
      {expanded && (
        <div className="mt-3 pl-11 text-sm text-gray-400 space-y-1">
          {slide.body && <p className="line-clamp-3">{slide.body}</p>}
          {slide.image_placeholder && (
            <p className="text-xs text-pink-400/80 italic">🖼 配图: {slide.image_placeholder}</p>
          )}
          {slide.bullet_points && (
            <ul className="list-disc pl-4 space-y-0.5">
              {slide.bullet_points.map((b, j) => (
                <li key={j}>{b}</li>
              ))}
            </ul>
          )}
          {slide.speaker_notes && (
            <p className="text-xs text-gray-600 italic mt-2">📝 {slide.speaker_notes}</p>
          )}
        </div>
      )}
    </div>
  )
}
