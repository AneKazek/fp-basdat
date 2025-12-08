import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ArrowLeft, Wallet, Save, Loader2 } from "lucide-react"
import { Link, useNavigate } from "react-router-dom"
import api from '../services/api';

export default function Register() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    address: "",
    owner: "",
    network: "",
    label: ""
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    
    try {
      await api.post('/wallet/register', {
        address: formData.address,
        owner_name: formData.owner,
        label: formData.label,
        network: formData.network
      })
      navigate(`/wallet/${formData.address}`)
    } catch (err: any) {
      console.error(err)
      setError(err.response?.data?.detail || 'Gagal mendaftarkan wallet. Pastikan data valid dan server berjalan.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-900 p-4 md:p-8">
      {/* Animated background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-20 w-72 h-72 bg-purple-600/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-purple-500/10 rounded-full blur-3xl animate-pulse delay-500"></div>
      </div>

      <div className="max-w-3xl mx-auto space-y-6 relative z-10">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Link to="/tracker">
            <Button variant="ghost" size="sm" className="gap-2 text-gray-300 hover:text-white hover:bg-gray-800/50">
              <ArrowLeft className="w-4 h-4" />
              Kembali
            </Button>
          </Link>
        </div>

        {/* Registration Form Card */}
        <Card className="backdrop-blur-xl bg-gray-900/70 border-gray-700/50 shadow-2xl">
          <CardHeader className="space-y-4">
            <div className="mx-auto w-16 h-16 bg-gradient-to-br from-purple-600 to-fuchsia-600 rounded-2xl flex items-center justify-center shadow-lg">
              <Wallet className="w-8 h-8 text-white" />
            </div>
            <div className="text-center">
              <CardTitle className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                Daftarkan Wallet Baru
              </CardTitle>
              <CardDescription className="text-base mt-2 text-gray-400">
                Tambahkan informasi wallet untuk tracking yang lebih mudah
              </CardDescription>
            </div>
            {error && (
              <div className="bg-red-500/10 border border-red-500/50 text-red-400 p-3 rounded-lg text-sm text-center">
                {error}
              </div>
            )}
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Address Field */}
              <div className="space-y-2">
                <Label htmlFor="address" className="text-sm font-medium text-gray-300">
                  Address Wallet <span className="text-red-400">*</span>
                </Label>
                <Input
                  id="address"
                  type="text"
                  placeholder="0x..."
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  required
                  className="h-12 bg-gray-800/50 backdrop-blur-sm border-gray-700 text-white placeholder:text-gray-500 focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500"
                />
                <p className="text-xs text-gray-400">
                  Masukkan alamat Ethereum wallet yang valid
                </p>
              </div>

              {/* Owner Field */}
              <div className="space-y-2">
                <Label htmlFor="owner" className="text-sm font-medium text-gray-300">
                  Owner <span className="text-red-400">*</span>
                </Label>
                <Input
                  id="owner"
                  type="text"
                  placeholder="Nama pemilik wallet"
                  value={formData.owner}
                  onChange={(e) => setFormData({ ...formData, owner: e.target.value })}
                  required
                  className="h-12 bg-gray-800/50 backdrop-blur-sm border-gray-700 text-white placeholder:text-gray-500 focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500"
                />
              </div>

              {/* Network Field */}
              <div className="space-y-2">
                <Label htmlFor="network" className="text-sm font-medium text-gray-300">
                  Network <span className="text-red-400">*</span>
                </Label>
                <Select
                  value={formData.network}
                  onValueChange={(value) => setFormData({ ...formData, network: value })}
                  required
                >
                  <SelectTrigger className="h-12 bg-gray-800/50 backdrop-blur-sm border-gray-700 text-white focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500">
                    <SelectValue placeholder="Pilih network" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="ethereum-mainnet">Ethereum Mainnet</SelectItem>
                    <SelectItem value="sepolia-testnet">Sepolia Testnet</SelectItem>
                    <SelectItem value="goerli-testnet">Goerli Testnet</SelectItem>
                    <SelectItem value="polygon-mainnet">Polygon Mainnet</SelectItem>
                    <SelectItem value="polygon-mumbai">Polygon Mumbai</SelectItem>
                    <SelectItem value="bsc-mainnet">BSC Mainnet</SelectItem>
                    <SelectItem value="bsc-testnet">BSC Testnet</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Label Field */}
              <div className="space-y-2">
                <Label htmlFor="label" className="text-sm font-medium text-gray-300">
                  Label <span className="text-red-400">*</span>
                </Label>
                <Input
                  id="label"
                  type="text"
                  placeholder="Contoh: Main Wallet, Trading Wallet, dll"
                  value={formData.label}
                  onChange={(e) => setFormData({ ...formData, label: e.target.value })}
                  required
                  className="h-12 bg-gray-800/50 backdrop-blur-sm border-gray-700 text-white placeholder:text-gray-500 focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500"
                />
                <p className="text-xs text-gray-400">
                  Berikan label untuk memudahkan identifikasi wallet
                </p>
              </div>

              {/* Submit Button */}
              <div className="pt-4">
                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full h-14 text-lg font-semibold bg-gradient-to-r from-purple-600 to-fuchsia-600 hover:from-purple-700 hover:to-fuchsia-700 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  ) : (
                    <Save className="w-5 h-5 mr-2" />
                  )}
                  {loading ? 'Mendaftarkan...' : 'Daftarkan Wallet'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Info Card */}
        <Card className="backdrop-blur-xl bg-cyan-500/10 border-cyan-500/30">
          <CardContent className="pt-6">
            <div className="flex gap-3">
              <div className="shrink-0 w-8 h-8 rounded-full bg-cyan-500/20 flex items-center justify-center">
                <span className="text-cyan-400 font-bold">i</span>
              </div>
              <div className="space-y-1">
                <p className="text-sm font-medium text-cyan-100">
                  Informasi Penting
                </p>
                <p className="text-sm text-cyan-200/80">
                  Pastikan alamat wallet yang Anda masukkan valid dan dapat diakses. Data yang didaftarkan akan memudahkan Anda dalam melakukan tracking transaksi wallet.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
