import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  ArrowLeft, Download, RefreshCw, Maximize2, Minimize2,
  Monitor, Smartphone, Tablet, Loader2, Copy, CheckCheck,
  Edit3, Eye, Code, Grid3X3
} from 'lucide-react'
import useStore from '../store/useStore'
import { api } from '../services/api'

const VIEWPORT_SIZES = {
  desktop: { width: 1280, height: 720, label: '桌面', icon: Monitor },
  tablet: { width: 1024, height: 576, label: '平板', icon: Tablet },
  mobile: { width: 640, height: 360, label: '手机', icon: Smartphone },
}

export default function PreviewPage() {
  const navigate = useNavigate()
  const { outline, style, theme } = useStore()
  const [htmlContent, setHtmlContent] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [viewport, setViewport] = useState('desktop')
  const [fullscreen, setFullscreen] = useState(false)
  const [viewMode, setViewMode] = useState('preview') // preview | code
  const [copied, setCopied] = useState(false)
  const [activeBg, setActiveBg] = useState('gradient')
  const iframeRef = useRef(null)
  const containerRef = useRef(null)

  // Redirect if no outline
  useEffect(() => {
    if (!outline) {
      navigate('/generate')
    }
  }, [outline, navigate])

  // Generate HTML on mount
  useEffect(() => {
    if (outline) {
      generateHTML()
    }
  }, [outline])

  const generateHTML = async (bgType = activeBg) => {
    setLoading(true)
    setError(null)
    try {
      const html = await api.renderHTML(outline, bgType)
      setHtmlContent(html)
      setActiveBg(bgType)
    } catch (err) {
      setError(err.message || String(err))
    } finally {
      setLoading(false)
    }
  }

  const switchBg = (bgType) => {
    setActiveBg(bgType)
    generateHTML(bgType)
  }

  const handleDownload = () => {
    if (!htmlContent) return
    const blob = new Blob([htmlContent], { type: 'text/html;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${outline?.title || 'presentation'}.html`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const handleCopyHTML = async () => {
    if (!htmlContent) return
    await navigator.clipboard.writeText(htmlContent)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const toggleFullscreen = () => {
    if (!containerRef.current) return
    if (!fullscreen) {
      containerRef.current.requestFullscreen?.()
    } else {
      document.exitFullscreen?.()
    }
    setFullscreen(!fullscreen)
  }

  const vp = VIEWPORT_SIZES[viewport]

  if (!outline) return null

  return (
    <div className="min-h-screen flex flex-col">
      {/* Toolbar */}
      <header className="border-b border-gray-800 bg-gray-950/90 backdrop-blur sticky top-0 z-50">
        <div className="max-w-full mx-auto px-6 py-3 flex items-center justify-between gap-4 flex-wrap">
          {/* Left */}
          <div className="flex items-center gap-3">
            <button onClick={() => navigate('/generate')} className="btn-icon">
              <ArrowLeft size={18} />
            </button>
            <div>
              <h1 className="text-sm font-semibold truncate max-w-[300px]">{outline.title}</h1>
              <p className="text-xs text-gray-500">{outline.slides.length} 页 · {style === 'style-a' ? '杂志风' : '瑞士风'}</p>
            </div>
          </div>

          {/* Center: View Mode */}
          <div className="flex items-center bg-gray-900 rounded-lg border border-gray-800 p-0.5">
            <button
              onClick={() => setViewMode('preview')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium transition-colors ${
                viewMode === 'preview' ? 'bg-gray-700 text-white' : 'text-gray-400 hover:text-gray-300'
              }`}
            >
              <Eye size={14} /> 预览
            </button>
            <button
              onClick={() => setViewMode('code')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium transition-colors ${
                viewMode === 'code' ? 'bg-gray-700 text-white' : 'text-gray-400 hover:text-gray-300'
              }`}
            >
              <Code size={14} /> 源码
            </button>
          </div>

          {/* Right: Actions */}
          <div className="flex items-center gap-2">
            {/* Viewport toggle */}
            <div className="flex items-center bg-gray-900 rounded-lg border border-gray-800 p-0.5">
              {Object.entries(VIEWPORT_SIZES).map(([key, { icon: Icon, label }]) => (
                <button
                  key={key}
                  onClick={() => setViewport(key)}
                  className={`p-1.5 rounded transition-colors ${
                    viewport === key ? 'bg-gray-700 text-white' : 'text-gray-500 hover:text-gray-300'
                  }`}
                  title={label}
                >
                  <Icon size={14} />
                </button>
              ))}
            </div>

            <button onClick={handleCopyHTML} className="btn-icon flex items-center gap-1.5" title="复制HTML源码">
              {copied ? <CheckCheck size={16} className="text-green-400" /> : <Copy size={16} />}
            </button>

            <button onClick={toggleFullscreen} className="btn-icon" title="全屏">
              {fullscreen ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
            </button>

            {/* Background type switcher */}
            <div className="flex items-center bg-gray-900 rounded-lg border border-gray-800 p-0.5">
              {[
                { v: 'gradient', l: '渐变' },
                { v: 'photo', l: '照片' },
                { v: 'pattern', l: '几何' },
                { v: 'none', l: '无' },
              ].map(({ v, l }) => (
                <button
                  key={v}
                  onClick={() => switchBg(v)}
                  className={`px-2 py-1 text-[10px] rounded font-medium transition-colors ${
                    activeBg === v ? 'bg-purple-600 text-white' : 'text-gray-500 hover:text-gray-300'
                  }`}
                >{l}</button>
              ))}
            </div>

            <button onClick={() => generateHTML(activeBg)} className="btn-icon" title="重新渲染" disabled={loading}>
              <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
            </button>

            <button onClick={handleDownload} className="btn-primary flex items-center gap-2 text-sm" disabled={!htmlContent}>
              <Download size={16} /> 下载 HTML
            </button>
          </div>
        </div>
      </header>

      {/* Preview Area */}
      <main
        ref={containerRef}
        className={`flex-1 flex items-center justify-center p-4 ${
          fullscreen ? 'bg-gray-950' : 'bg-gray-950'
        }`}
      >
        {loading && !htmlContent ? (
          <div className="flex flex-col items-center gap-4 text-gray-400">
            <Loader2 size={40} className="animate-spin text-blue-400" />
            <p>正在渲染 HTML...</p>
          </div>
        ) : error ? (
          <div className="card border-red-500/30 bg-red-500/5 max-w-md text-center">
            <p className="text-red-400 mb-4">{error}</p>
            <button onClick={generateHTML} className="btn-primary text-sm">重试</button>
          </div>
        ) : viewMode === 'code' ? (
          /* Code View */
          <div className="w-full max-w-5xl h-[80vh] overflow-auto bg-gray-900 border border-gray-800 rounded-xl">
            <pre className="p-6 text-xs text-gray-300 font-mono whitespace-pre-wrap break-all">
              {htmlContent}
            </pre>
          </div>
        ) : (
          /* Preview */
          <div
            className="relative overflow-hidden rounded-lg shadow-2xl transition-all duration-300"
            style={{
              width: fullscreen ? '100%' : Math.min(vp.width, window.innerWidth - 48),
              height: fullscreen ? '100%' : Math.min(vp.height, (window.innerWidth - 48) * vp.height / vp.width),
              maxWidth: vp.width,
              maxHeight: vp.height,
            }}
          >
            {htmlContent ? (
              <iframe
                ref={iframeRef}
                srcDoc={htmlContent}
                className="w-full h-full border-0"
                title="PPT Preview"
                sandbox="allow-scripts allow-same-origin"
              />
            ) : (
              <div className="w-full h-full bg-gray-900 flex items-center justify-center text-gray-600">
                加载中...
              </div>
            )}
          </div>
        )}
      </main>

      {/* Slide Thumbnails Strip */}
      {viewMode === 'preview' && htmlContent && !fullscreen && (
        <footer className="border-t border-gray-800 bg-gray-950/90 py-3 px-6">
          <div className="flex items-center gap-2 overflow-x-auto pb-1 max-w-full">
            {outline.slides.map((slide, i) => (
              <div
                key={i}
                className="shrink-0 w-24 h-14 bg-gray-900 border border-gray-800 rounded flex flex-col items-center justify-center text-[10px] text-gray-500 hover:border-gray-700 transition-colors cursor-pointer"
                title={slide.title || `第${i + 1}页`}
              >
                <span className="text-gray-400 font-semibold">{i + 1}</span>
                <span className="truncate px-1 max-w-full">{slide.layout}</span>
              </div>
            ))}
          </div>
          <p className="text-[10px] text-gray-600 text-center mt-2">
            提示：在预览中使用 ← → 方向键翻页 · ESC 切换网格线（瑞士风）· 滚轮翻页
          </p>
        </footer>
      )}
    </div>
  )
}
