import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Search as SearchIcon, Wallet, PlusCircle } from "lucide-react"
import { useNavigate } from "react-router-dom"

export default function Search() {
  const navigate = useNavigate()
  const [address, setAddress] = useState("0xfbd3aea6648db6df4895828bc58388709e779a1e")

  const handleSearch = () => {
    if (address.trim()) {
      navigate(`/wallet/${address}`)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-900 flex items-center justify-center p-4">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-20 w-72 h-72 bg-purple-600/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-purple-500/10 rounded-full blur-3xl animate-pulse delay-500"></div>
      </div>

      <div className="w-full max-w-2xl relative z-10 space-y-4">
        {/* Main Tracker Card */}
        <Card className="backdrop-blur-xl bg-gray-900/70 border-gray-700/50 shadow-2xl">
          <CardHeader className="text-center space-y-4 pb-8">
            <div className="mx-auto w-16 h-16 bg-gradient-to-br from-purple-600 to-fuchsia-600 rounded-2xl flex items-center justify-center shadow-lg">
              <Wallet className="w-8 h-8 text-white" />
            </div>
            <CardTitle className="text-4xl font-bold text-white">
              Ethereum Wallet Tracker
            </CardTitle>
            <CardDescription className="text-lg text-gray-400">
              Masukkan alamat Ethereum untuk melacak transaksi dan informasi wallet
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-300">
                Alamat Wallet
              </label>
              <div className="relative">
                <Input
                  type="text"
                  placeholder="0x..."
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                  className="pl-4 pr-12 h-14 text-base bg-gray-800/50 backdrop-blur-sm border-gray-600 text-white placeholder:text-gray-500 focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500 transition-all"
                />
                <SearchIcon className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
              </div>
            </div>

            <Button 
              onClick={handleSearch}
              className="w-full h-14 text-lg font-semibold bg-gradient-to-r from-purple-600 to-fuchsia-600 hover:from-purple-700 hover:to-fuchsia-700 text-white shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-[1.02]"
            >
              <SearchIcon className="w-5 h-5 mr-2" />
              Lacak Wallet
            </Button>

            <Button 
              onClick={() => navigate("/register")}
              variant="outline"
              className="w-full h-14 text-lg font-semibold border-2 border-gray-600 text-gray-300 hover:bg-gray-800/50 hover:text-white hover:border-gray-500 transition-all duration-300"
            >
              <PlusCircle className="w-5 h-5 mr-2" />
              Daftarkan Wallet
            </Button>

            <div className="pt-4 border-t border-gray-700">
              <p className="text-sm text-gray-500 text-center">
                Contoh: 0xfbd3aea6648db6df4895828bc58388709e779a1e
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
