import { Link } from 'react-router-dom'
import HeroAnimation from '@/components/landing/HeroAnimation'
import StatsCounter from '@/components/landing/StatsCounter'
import FeatureCard from '@/components/landing/FeatureCard'
import TechStack from '@/components/landing/TechStack'
import MobileNav from '@/components/landing/MobileNav'
import {
  CpuChipIcon,
  CircleStackIcon,
  CubeIcon,
  CheckCircleIcon,
  CodeBracketIcon,
  RocketLaunchIcon,
} from '@heroicons/react/24/outline'

export default function Landing() {
  return (
    <div className="min-h-screen bg-slate-900 text-white overflow-hidden">
      <MobileNav />
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center">
        <HeroAnimation />

        <div className="relative z-10 max-w-6xl mx-auto px-6 text-center">
          <h1 className="text-6xl md:text-8xl font-bold mb-6">
            <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              GPU-Accelerated
            </span>
            <br />
            <span className="text-white">Microscopy Analysis</span>
          </h1>

          <p className="text-xl md:text-2xl text-slate-300 mb-8 max-w-3xl mx-auto">
            Open source, 100× faster Z-stack analysis with human-in-the-loop
            validation. Built for scientists who value both speed and accuracy.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
            <Link
              to="/app"
              className="px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg font-semibold text-lg hover:shadow-lg hover:shadow-purple-500/50 transition-all duration-300 hover:scale-105"
            >
              Try Demo
            </Link>
            <a
              href="https://github.com/yourusername/zstack-analyzer"
              target="_blank"
              rel="noopener noreferrer"
              className="px-8 py-4 bg-slate-800 border border-slate-700 rounded-lg font-semibold text-lg hover:border-blue-500/50 transition-all duration-300 hover:scale-105"
            >
              View on GitHub
            </a>
          </div>

          {/* Floating Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            <StatsCounter end={100} suffix="+" label="Z-stacks/hour" />
            <StatsCounter end={500} suffix="ms" label="Latency" prefix="<" />
            <StatsCounter end={95} suffix="%" label="Accuracy" />
          </div>
        </div>

        {/* Scroll indicator */}
        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
          <svg
            className="w-6 h-6 text-slate-400"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path d="M19 14l-7 7m0 0l-7-7m7 7V3"></path>
          </svg>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 px-6 bg-slate-950/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-5xl font-bold mb-4">Built for Performance</h2>
            <p className="text-xl text-slate-400">
              Everything you need for high-throughput microscopy analysis
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <FeatureCard
              icon={<CpuChipIcon className="w-8 h-8 text-white" />}
              title="GPU Processing"
              description="Harness the power of tinygrad for blazing-fast inference. Process entire Z-stacks in milliseconds, not minutes."
              delay={0}
            />
            <FeatureCard
              icon={<CircleStackIcon className="w-8 h-8 text-white" />}
              title="Multi-format Support"
              description="TIFF, CZI, ND2, and more. Import your data without conversion headaches."
              delay={0.1}
            />
            <FeatureCard
              icon={<CubeIcon className="w-8 h-8 text-white" />}
              title="3D Visualization"
              description="Interactive WebGL rendering with real-time manipulation. See your data from every angle."
              delay={0.2}
            />
            <FeatureCard
              icon={<CheckCircleIcon className="w-8 h-8 text-white" />}
              title="Human Validation"
              description="AI suggests, you decide. Built-in review queue keeps you in control of critical decisions."
              delay={0.3}
            />
            <FeatureCard
              icon={<CodeBracketIcon className="w-8 h-8 text-white" />}
              title="Open Source"
              description="MIT licensed. Extend, modify, and integrate however you need. No vendor lock-in."
              delay={0.4}
            />
            <FeatureCard
              icon={<RocketLaunchIcon className="w-8 h-8 text-white" />}
              title="Scalable"
              description="From single workstation to cluster deployment. Scales with your research needs."
              delay={0.5}
            />
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-5xl font-bold mb-4">How It Works</h2>
            <p className="text-xl text-slate-400">
              Three simple steps to publication-ready analysis
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            {/* Step 1 */}
            <div className="relative">
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-500/20 border-2 border-blue-500 text-2xl font-bold mb-6">
                  1
                </div>
                <h3 className="text-2xl font-bold mb-4">Upload</h3>
                <p className="text-slate-400 mb-6">
                  Drag and drop your Z-stack images. Batch processing supported
                  for high-throughput workflows.
                </p>
                <div className="h-48 bg-slate-800/50 rounded-lg border border-slate-700/50 flex items-center justify-center">
                  <div className="text-6xl">📁</div>
                </div>
              </div>

              {/* Arrow */}
              <div className="hidden md:block absolute top-8 -right-6 text-blue-500">
                <svg
                  className="w-12 h-12"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 7l5 5m0 0l-5 5m5-5H6"
                  />
                </svg>
              </div>
            </div>

            {/* Step 2 */}
            <div className="relative">
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-purple-500/20 border-2 border-purple-500 text-2xl font-bold mb-6">
                  2
                </div>
                <h3 className="text-2xl font-bold mb-4">Process</h3>
                <p className="text-slate-400 mb-6">
                  GPU-accelerated inference runs automatically. Watch real-time
                  progress as each stack is analyzed.
                </p>
                <div className="h-48 bg-slate-800/50 rounded-lg border border-slate-700/50 flex items-center justify-center">
                  <div className="text-6xl">⚡</div>
                </div>
              </div>

              {/* Arrow */}
              <div className="hidden md:block absolute top-8 -right-6 text-purple-500">
                <svg
                  className="w-12 h-12"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 7l5 5m0 0l-5 5m5-5H6"
                  />
                </svg>
              </div>
            </div>

            {/* Step 3 */}
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-pink-500/20 border-2 border-pink-500 text-2xl font-bold mb-6">
                3
              </div>
              <h3 className="text-2xl font-bold mb-4">Validate</h3>
              <p className="text-slate-400 mb-6">
                Review AI predictions, make corrections, and export results.
                Your feedback improves future accuracy.
              </p>
              <div className="h-48 bg-slate-800/50 rounded-lg border border-slate-700/50 flex items-center justify-center">
                <div className="text-6xl">✅</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Performance Section */}
      <section id="performance" className="py-24 px-6 bg-slate-950/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-5xl font-bold mb-4">Performance That Matters</h2>
            <p className="text-xl text-slate-400">
              Benchmarked against industry standards
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            {/* Speed Comparison */}
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-8">
              <h3 className="text-2xl font-bold mb-6">Processing Speed</h3>
              <div className="space-y-6">
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-slate-400">ImageJ</span>
                    <span className="font-mono">2.5s</span>
                  </div>
                  <div className="h-4 bg-slate-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-slate-500"
                      style={{ width: '100%' }}
                    />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-slate-400">CellProfiler</span>
                    <span className="font-mono">1.8s</span>
                  </div>
                  <div className="h-4 bg-slate-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-slate-500"
                      style={{ width: '72%' }}
                    />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-blue-400 font-semibold">
                      Z-Stack Analyzer
                    </span>
                    <span className="font-mono text-blue-400">0.025s</span>
                  </div>
                  <div className="h-4 bg-slate-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-blue-500 to-purple-600"
                      style={{ width: '1%' }}
                    />
                  </div>
                </div>
              </div>
              <p className="text-slate-500 text-sm mt-4">
                Tested on 512×512×50 Z-stacks, NVIDIA RTX 3090
              </p>
            </div>

            {/* Memory Efficiency */}
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-8">
              <h3 className="text-2xl font-bold mb-6">Memory Efficiency</h3>
              <div className="space-y-6">
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-slate-400">ImageJ</span>
                    <span className="font-mono">4.2 GB</span>
                  </div>
                  <div className="h-4 bg-slate-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-slate-500"
                      style={{ width: '100%' }}
                    />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-slate-400">CellProfiler</span>
                    <span className="font-mono">3.1 GB</span>
                  </div>
                  <div className="h-4 bg-slate-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-slate-500"
                      style={{ width: '74%' }}
                    />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-blue-400 font-semibold">
                      Z-Stack Analyzer
                    </span>
                    <span className="font-mono text-blue-400">0.8 GB</span>
                  </div>
                  <div className="h-4 bg-slate-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-blue-500 to-purple-600"
                      style={{ width: '19%' }}
                    />
                  </div>
                </div>
              </div>
              <p className="text-slate-500 text-sm mt-4">
                Peak VRAM usage during inference
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Tech Stack Section */}
      <section className="py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-5xl font-bold mb-4">Modern Tech Stack</h2>
            <p className="text-xl text-slate-400">
              Built with cutting-edge tools for maximum performance
            </p>
          </div>

          <TechStack />

          <div className="mt-12 text-center">
            <p className="text-slate-400 mb-4">
              Powered by tinygrad for GPU acceleration, React for UI, and
              FastAPI for backend services.
            </p>
            <a
              href="https://docs.zstack-analyzer.dev"
              className="text-blue-400 hover:text-blue-300 font-medium"
            >
              Read the technical documentation →
            </a>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-6 bg-gradient-to-br from-blue-900/20 via-purple-900/20 to-pink-900/20">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-5xl font-bold mb-6">
            Ready to analyze your data?
          </h2>
          <p className="text-xl text-slate-300 mb-8">
            Join researchers using GPU-accelerated microscopy analysis. Start
            processing Z-stacks 100× faster today.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <Link
              to="/app"
              className="px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg font-semibold text-lg hover:shadow-lg hover:shadow-purple-500/50 transition-all duration-300 hover:scale-105"
            >
              Launch Application
            </Link>
            <a
              href="https://github.com/yourusername/zstack-analyzer"
              target="_blank"
              rel="noopener noreferrer"
              className="px-8 py-4 bg-slate-800 border border-slate-700 rounded-lg font-semibold text-lg hover:border-blue-500/50 transition-all duration-300 hover:scale-105 flex items-center justify-center gap-2"
            >
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
              </svg>
              Star on GitHub
            </a>
          </div>

          <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg border border-slate-700/50 p-8 max-w-md mx-auto">
            <h3 className="text-xl font-semibold mb-4">Get Updates</h3>
            <p className="text-slate-400 text-sm mb-4">
              Stay informed about new features and improvements
            </p>
            <form className="flex gap-2">
              <input
                type="email"
                placeholder="your@email.com"
                className="flex-1 px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg focus:outline-none focus:border-blue-500"
              />
              <button
                type="submit"
                className="px-6 py-2 bg-blue-500 hover:bg-blue-600 rounded-lg font-semibold transition-colors"
              >
                Subscribe
              </button>
            </form>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t border-slate-800">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center">
          <div className="text-slate-400 text-sm mb-4 md:mb-0">
            © 2024 Z-Stack Analyzer. MIT Licensed.
          </div>
          <div className="flex gap-6">
            <a
              href="https://github.com/yourusername/zstack-analyzer"
              className="text-slate-400 hover:text-white transition-colors"
            >
              GitHub
            </a>
            <a
              href="https://docs.zstack-analyzer.dev"
              className="text-slate-400 hover:text-white transition-colors"
            >
              Documentation
            </a>
            <a
              href="https://discord.gg/zstack"
              className="text-slate-400 hover:text-white transition-colors"
            >
              Community
            </a>
          </div>
        </div>
      </footer>
    </div>
  )
}
