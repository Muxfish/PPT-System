import { useNavigate } from 'react-router-dom'
import { Sparkles, Palette, FileText, Layout, ArrowRight } from 'lucide-react'
import useStore from '../store/useStore'

const features = [
  {
    icon: Sparkles,
    title: 'AI 智能生成',
    desc: '基于 DeepSeek 大模型，输入主题即可自动生成专业PPT大纲和内容',
  },
  {
    icon: Palette,
    title: '双重视觉风格',
    desc: '电子杂志 × 电子墨水风格 vs 瑞士国际主义风格，满足不同场景需求',
  },
  {
    icon: Layout,
    title: '多套配色主题',
    desc: '每种风格内置多套精选配色，墨水经典、靛蓝瓷、IKB克莱因蓝等',
  },
  {
    icon: FileText,
    title: '单文件 HTML 导出',
    desc: '生成完整的单文件 HTML，支持键盘翻页、触屏滑动、滚轮导航',
  },
]

const testimonials = [
  { quote: '适合线下分享、私享会、Demo Day、AI产品发布', label: '产品发布场景' },
  { quote: '杂志级的版面设计，让每份PPT都有独特的叙事感', label: '设计品质' },
  { quote: '网格系统确保版式一致性，16列精确定位', label: '瑞士风特色' },
]

export default function HomePage() {
  const navigate = useNavigate()
  const setField = useStore((s) => s.setField)

  const handleQuickStart = (style) => {
    setField('style', style)
    setField('theme', style === 'style-a' ? 'ink-classic' : 'ikb-blue')
    navigate('/generate')
  }

  return (
    <div className="min-h-screen">
      {/* Hero */}
      <header className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-900/30 via-gray-950 to-gray-950" />
        <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-blue-600/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-purple-600/10 rounded-full blur-3xl" />

        <div className="relative max-w-5xl mx-auto px-6 py-24 text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600/20 border border-blue-500/30 rounded-full text-blue-400 text-sm mb-8">
            <Sparkles size={16} />
            Powered by DeepSeek + LangChain
          </div>

          <h1 className="text-5xl md:text-6xl font-bold tracking-tight mb-6 leading-tight">
            高级
            <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              PPT
            </span>
            生成系统
          </h1>

          <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed">
            融合歸藏老师 10 年设计经验的开源 PPT Skill，
            基于大模型智能生成杂志级 HTML 演示文稿。支持电子杂志风 × 瑞士国际主义风双重视觉系统。
          </p>

          <div className="flex items-center justify-center gap-4 flex-wrap">
            <button
              onClick={() => handleQuickStart('style-b')}
              className="btn-primary flex items-center gap-2 text-lg px-8 py-4"
            >
              瑞士风 PPT <ArrowRight size={20} />
            </button>
            <button
              onClick={() => handleQuickStart('style-a')}
              className="btn-secondary flex items-center gap-2 text-lg px-8 py-4"
            >
              杂志风 PPT <ArrowRight size={20} />
            </button>
          </div>
        </div>
      </header>

      {/* Features */}
      <section className="max-w-6xl mx-auto px-6 py-20">
        <h2 className="text-3xl font-bold text-center mb-12">核心能力</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((f, i) => (
            <div key={i} className="card group hover:border-gray-700 transition-colors">
              <div className="w-12 h-12 bg-blue-600/20 rounded-lg flex items-center justify-center mb-4 group-hover:bg-blue-600/30 transition-colors">
                <f.icon size={24} className="text-blue-400" />
              </div>
              <h3 className="text-lg font-semibold mb-2">{f.title}</h3>
              <p className="text-gray-400 text-sm leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Style Overview */}
      <section className="max-w-6xl mx-auto px-6 py-20 border-t border-gray-800">
        <h2 className="text-3xl font-bold text-center mb-12">双重视觉系统</h2>
        <div className="grid md:grid-cols-2 gap-8">
          {/* Style A */}
          <div className="card p-8 hover:border-gray-700 transition-colors cursor-pointer"
               onClick={() => handleQuickStart('style-a')}>
            <div className="flex items-center gap-3 mb-4">
              <span className="text-xs font-bold text-orange-400 bg-orange-400/10 px-2 py-1 rounded">Style A</span>
              <h3 className="text-xl font-bold">电子杂志 × 电子墨水</h3>
            </div>
            <p className="text-gray-400 text-sm mb-6 leading-relaxed">
              Monocle 杂志风、衬线字体、大片留白、叙事感强。适合个人分享、观点表达、线下私享会。
            </p>
            <div className="flex flex-wrap gap-2">
              {['墨水经典', '靛蓝瓷', '森林墨', '牛皮纸', '沙丘'].map((t) => (
                <span key={t} className="px-2 py-1 bg-gray-800 rounded text-xs text-gray-400">{t}</span>
              ))}
            </div>
            <div className="mt-4 h-32 rounded-lg bg-gradient-to-br from-[#faf8f5] to-[#e8e0d5] flex items-center justify-center">
              <span className="font-serif text-2xl text-[#1a1a1a] opacity-40">Editorial Style</span>
            </div>
          </div>

          {/* Style B */}
          <div className="card p-8 hover:border-gray-700 transition-colors cursor-pointer"
               onClick={() => handleQuickStart('style-b')}>
            <div className="flex items-center gap-3 mb-4">
              <span className="text-xs font-bold text-blue-400 bg-blue-400/10 px-2 py-1 rounded">Style B</span>
              <h3 className="text-xl font-bold">瑞士国际主义</h3>
            </div>
            <p className="text-gray-400 text-sm mb-6 leading-relaxed">
              16列网格、直角、1px发丝线、单一高饱和锚点色、无渐变无阴影。适合产品分析、方法论、AI产品发布。
            </p>
            <div className="flex flex-wrap gap-2">
              {['IKB克莱因蓝', '柠檬黄', '柠檬绿', '安全橙'].map((t) => (
                <span key={t} className="px-2 py-1 bg-gray-800 rounded text-xs text-gray-400">{t}</span>
              ))}
            </div>
            <div className="mt-4 h-32 rounded-lg bg-white flex items-center justify-center border border-gray-200">
              <span className="font-sans text-2xl text-[#1a1a1a] opacity-40 font-bold">Swiss Style</span>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="max-w-6xl mx-auto px-6 py-20 border-t border-gray-800">
        <div className="grid md:grid-cols-3 gap-6">
          {testimonials.map((t, i) => (
            <div key={i} className="card text-center p-8">
              <p className="text-gray-300 text-lg italic mb-4">"{t.quote}"</p>
              <span className="text-xs text-gray-500 uppercase tracking-wider">{t.label}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-8 text-center text-gray-600 text-sm">
        <p>基于 <a href="https://github.com/op7418/guizang-ppt-skill" className="text-blue-400 hover:underline" target="_blank" rel="noopener">guizang-ppt-skill</a> 设计理念构建 · Powered by DeepSeek</p>
      </footer>
    </div>
  )
}
