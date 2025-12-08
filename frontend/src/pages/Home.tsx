import { useState, useEffect } from "react"
import { Link } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Wallet, Search, TrendingUp, Shield, Zap, TrendingDown } from "lucide-react"
import { AreaChart, Area, Tooltip, ResponsiveContainer } from 'recharts';

interface EthPrice {
  usd: number
  usd_24h_change: number
}

export default function Home() {
  const [ethPrice, setEthPrice] = useState<EthPrice | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [chartData, setChartData] = useState<any[]>([])

  useEffect(() => {
    const fetchEthPrice = async () => {
      try {
        const response = await fetch(
          "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd&include_24hr_change=true"
        )
        const data = await response.json()
        setEthPrice({
          usd: data.ethereum.usd,
          usd_24h_change: data.ethereum.usd_24h_change
        })
        
        // Generate gimmick chart data based on current price
        // This creates a realistic-looking 24h trend curve
        const basePrice = data.ethereum.usd
        const volatility = basePrice * 0.02 // 2% volatility
        const points = 24
        const newChartData = Array.from({ length: points }, (_, i) => {
            const randomChange = (Math.random() - 0.5) * volatility
            return {
                time: `${i}:00`,
                price: basePrice + randomChange - (volatility/2) + (i * (data.ethereum.usd_24h_change > 0 ? 1 : -1) * (volatility/points))
            }
        })
        // Ensure last point matches current price closely
        newChartData[points-1].price = basePrice
        
        setChartData(newChartData)
        setIsLoading(false)
      } catch (error) {
        console.error("Failed to fetch ETH price:", error)
        setIsLoading(false)
      }
    }

    fetchEthPrice()
    const interval = setInterval(fetchEthPrice, 30000) // Update every 30 seconds

    return () => clearInterval(interval)
  }, [])

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(price)
  }

  const isPositive = ethPrice && ethPrice.usd_24h_change > 0

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-900">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-20 w-72 h-72 bg-purple-600/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-purple-500/10 rounded-full blur-3xl animate-pulse delay-500"></div>
      </div>

      <main className="relative z-10 px-4 py-16 md:py-24">
        <div className="max-w-7xl mx-auto">
          {/* Hero Section */}
          <div className="text-center mb-16 space-y-6">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-purple-600 to-fuchsia-600 rounded-3xl shadow-2xl mb-6">
              <Wallet className="w-10 h-10 text-white" />
            </div>
            <h1 className="text-5xl md:text-7xl font-bold leading-tight">
              <span className="text-white">Ethereum Wallet Tracker</span>
              <br />
              <span className="bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">Untuk Anda</span>
            </h1>
            <p className="text-xl md:text-2xl text-gray-300 max-w-3xl mx-auto leading-relaxed">
              Lacak transaksi Ethereum dengan mudah. Pantau wallet, analisis aktivitas, dan dapatkan insight real-time dari blockchain.
            </p>

            {/* Live ETH Price Monitor (Moved Here) */}
            <div className="max-w-4xl mx-auto mt-8 mb-12 transform hover:scale-[1.02] transition-transform duration-500">
                <Card className="backdrop-blur-xl bg-gray-900/80 border-gray-700/50 shadow-2xl overflow-hidden">
                    <div className="bg-gradient-to-r from-slate-900/50 via-purple-900/20 to-slate-900/50 p-1">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 p-6 items-center">
                            {/* Price Info */}
                            <div className="md:col-span-1 space-y-2 text-left">
                                <div className="flex items-center gap-3 mb-2">
                                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-400 to-blue-500 flex items-center justify-center shadow-lg">
                                        <span className="text-white font-bold text-lg">Ξ</span>
                                    </div>
                                    <div>
                                        <h3 className="text-white font-bold text-lg">Ethereum</h3>
                                        <p className="text-cyan-400 text-xs font-mono tracking-wider">ETH/USD</p>
                                    </div>
                                </div>
                                
                                {isLoading ? (
                                    <div className="animate-pulse space-y-2">
                                        <div className="h-8 w-32 bg-gray-700/50 rounded"></div>
                                        <div className="h-4 w-20 bg-gray-700/50 rounded"></div>
                                    </div>
                                ) : ethPrice ? (
                                    <div className="space-y-1">
                                        <div className="text-3xl font-bold text-white tracking-tight">
                                            {formatPrice(ethPrice.usd)}
                                        </div>
                                        <div className={`flex items-center gap-2 text-sm font-bold ${
                                            isPositive ? 'text-green-400' : 'text-red-400'
                                        }`}>
                                            <span className={`flex items-center px-2 py-0.5 rounded-full ${
                                                isPositive ? 'bg-green-500/10' : 'bg-red-500/10'
                                            }`}>
                                                {isPositive ? <TrendingUp className="w-3 h-3 mr-1" /> : <TrendingDown className="w-3 h-3 mr-1" />}
                                                {Math.abs(ethPrice.usd_24h_change).toFixed(2)}%
                                            </span>
                                            <span className="text-gray-500 text-xs">24h Change</span>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="text-gray-500">Failed to load price</div>
                                )}
                            </div>

                            {/* Gimmick Chart */}
                            <div className="md:col-span-2 h-[160px] w-full">
                                {isLoading ? (
                                    <div className="w-full h-full bg-gray-800/30 animate-pulse rounded-lg"></div>
                                ) : (
                                    <ResponsiveContainer width="100%" height="100%">
                                        <AreaChart data={chartData}>
                                            <defs>
                                                <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                                                    <stop offset="5%" stopColor={isPositive ? "#4ade80" : "#f87171"} stopOpacity={0.3}/>
                                                    <stop offset="95%" stopColor={isPositive ? "#4ade80" : "#f87171"} stopOpacity={0}/>
                                                </linearGradient>
                                            </defs>
                                            <Tooltip 
                                                contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#fff' }}
                                                itemStyle={{ color: '#fff' }}
                                                labelStyle={{ display: 'none' }}
                                                formatter={(value: number) => [`$${value.toFixed(2)}`, 'Price']}
                                            />
                                            <Area 
                                                type="monotone" 
                                                dataKey="price" 
                                                stroke={isPositive ? "#4ade80" : "#f87171"} 
                                                strokeWidth={2}
                                                fillOpacity={1} 
                                                fill="url(#colorPrice)" 
                                                animationDuration={2000}
                                            />
                                        </AreaChart>
                                    </ResponsiveContainer>
                                )}
                            </div>
                        </div>
                    </div>
                </Card>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-4">
              <Link to="/tracker">
                <Button size="lg" className="h-14 px-8 text-lg font-semibold bg-gradient-to-r from-purple-600 to-fuchsia-600 hover:from-purple-700 hover:to-fuchsia-700 text-white shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-105">
                  <Search className="w-5 h-5 mr-2" />
                  Mulai Tracking
                </Button>
              </Link>
              <Button size="lg" variant="outline" className="h-14 px-8 text-lg font-semibold bg-transparent border-2 border-gray-600 text-gray-300 hover:bg-gray-800/50 hover:text-white hover:border-gray-500">
                Pelajari Lebih Lanjut
              </Button>
            </div>
          </div>

          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl mx-auto">
            <Card className="backdrop-blur-xl bg-gray-900/70 border-gray-700/50 shadow-xl hover:shadow-2xl transition-all duration-300 hover:scale-105">
              <CardHeader>
                <div className="w-12 h-12 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-xl flex items-center justify-center mb-4">
                  <Search className="w-6 h-6 text-white" />
                </div>
                <CardTitle className="text-xl text-white">Pencarian Cepat</CardTitle>
                <CardDescription className="text-gray-400">
                  Cari wallet dengan address Ethereum dan dapatkan informasi detail dalam sekejap
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="backdrop-blur-xl bg-gray-900/70 border-gray-700/50 shadow-xl hover:shadow-2xl transition-all duration-300 hover:scale-105">
              <CardHeader>
                <div className="w-12 h-12 bg-gradient-to-br from-purple-600 to-fuchsia-600 rounded-xl flex items-center justify-center mb-4">
                  <TrendingUp className="w-6 h-6 text-white" />
                </div>
                <CardTitle className="text-xl text-white">Analisis Transaksi</CardTitle>
                <CardDescription className="text-gray-400">
                  Lihat riwayat transaksi lengkap dengan detail value, fee, dan timestamp
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="backdrop-blur-xl bg-gray-900/70 border-gray-700/50 shadow-xl hover:shadow-2xl transition-all duration-300 hover:scale-105">
              <CardHeader>
                <div className="w-12 h-12 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-xl flex items-center justify-center mb-4">
                  <Shield className="w-6 h-6 text-white" />
                </div>
                <CardTitle className="text-xl text-white">Aman & Terpercaya</CardTitle>
                <CardDescription className="text-gray-400">
                  Data langsung dari blockchain, tanpa menyimpan informasi pribadi Anda
                </CardDescription>
              </CardHeader>
            </Card>
          </div>

          {/* CTA Section */}
          <div className="mt-20">
            <Card className="backdrop-blur-xl bg-gradient-to-r from-purple-900/40 to-fuchsia-900/40 border-purple-700/50 shadow-2xl">
              <CardContent className="p-12 text-center">
                <Zap className="w-16 h-16 mx-auto mb-6 text-cyan-400" />
                <h2 className="text-3xl md:text-4xl font-bold mb-4">
                  <span className="text-white">Siap untuk </span>
                  <span className="bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">Melacak Wallet?</span>
                </h2>
                <p className="text-lg text-gray-300 mb-8 max-w-2xl mx-auto">
                  Masukkan address Ethereum dan dapatkan insight lengkap tentang aktivitas wallet dalam hitungan detik
                </p>
                <Link to="/tracker">
                  <Button size="lg" className="h-14 px-12 text-lg font-semibold bg-gradient-to-r from-purple-600 to-fuchsia-600 hover:from-purple-700 hover:to-fuchsia-700 text-white shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-105">
                    <Search className="w-5 h-5 mr-2" />
                    Mulai Sekarang
                  </Button>
                </Link>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}
