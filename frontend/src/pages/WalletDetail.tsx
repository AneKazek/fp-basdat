import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../services/api';
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ArrowLeft, Copy, PlusCircle, ChevronLeft, ChevronRight, Search } from "lucide-react"

interface TxItem {
  tx_hash: string;
  block_number: number;
  time_stamp: string;
  from_address: string;
  to_address?: string;
  value_eth: number;
  tx_fee_eth: number;
  direction: 'in' | 'out' | 'self';
  status: string;
}

interface WalletInfoResp {
  wallet: {
    wallet_id: number;
    address: string;
    label: string;
    owner_name?: string | null;
    network_name: string;
  };
  transactions: {
    page: number;
    pageSize: number;
    total: number;
    items: TxItem[];
  };
}

const WalletDetail: React.FC = () => {
  const { address } = useParams();
  const [data, setData] = useState<WalletInfoResp | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const pageSize = 10;

  useEffect(() => {
    const fetchData = async () => {
        if (!address) return;
        setLoading(true);
        try {
            const res = await api.get<WalletInfoResp>(`/wallet/${address}`, { 
              params: { page: currentPage, pageSize } 
            });
            setData(res.data);
            setError('');
        } catch (e: any) {
            setError(e.response?.data?.detail || 'Terjadi kesalahan');
        } finally {
            setLoading(false);
        }
    };
    fetchData();
  }, [address, currentPage]);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  if (loading) return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-900 flex items-center justify-center">
      <div className="animate-pulse text-white">Loading...</div>
    </div>
  );
  
  if (error) return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-900 flex items-center justify-center">
       <div className="text-red-500 bg-red-950/50 p-4 rounded-lg border border-red-800">{error}</div>
    </div>
  );

  if (!data) return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-900 flex items-center justify-center">
      <div className="text-white">Data not found</div>
    </div>
  );

  const totalPages = Math.ceil(data.transactions.total / pageSize);

  const filteredTransactions = data.transactions.items.filter(tx => 
    tx.tx_hash.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-900 p-4 md:p-8">
      {/* Animated background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-20 w-72 h-72 bg-purple-600/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
      </div>

      <div className="max-w-7xl mx-auto space-y-6 relative z-10">
        {/* Header */}
        <div className="flex items-center justify-between gap-4">
          <Link to="/">
            <Button variant="ghost" size="sm" className="gap-2 text-gray-300 hover:text-white hover:bg-gray-800/50">
              <ArrowLeft className="w-4 h-4" />
              Kembali
            </Button>
          </Link>
          <Link to="/register">
            <Button className="gap-2 bg-gradient-to-r from-purple-600 to-fuchsia-600 hover:from-purple-700 hover:to-fuchsia-700 shadow-lg">
              <PlusCircle className="w-4 h-4" />
              Daftarkan Wallet
            </Button>
          </Link>
        </div>

        {/* Wallet Summary Card */}
        <Card className="backdrop-blur-xl bg-gray-900/70 border-gray-700/50 shadow-2xl">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                Ringkasan Wallet
              </CardTitle>
              <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
                Aktif
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-gray-400 font-medium mb-2">Address</p>
                  <div className="flex items-center gap-2 p-3 bg-gray-800/50 rounded-lg backdrop-blur-sm border border-gray-700">
                    <code className="text-sm flex-1 break-all font-mono text-gray-300">{data.wallet.address}</code>
                    <Button 
                      size="sm" 
                      variant="ghost"
                      onClick={() => copyToClipboard(data.wallet.address)}
                      className="shrink-0 text-gray-400 hover:text-white hover:bg-gray-700/50"
                    >
                      <Copy className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
                <div>
                  <p className="text-sm text-gray-400 font-medium mb-2">Network</p>
                  <p className="text-base font-semibold text-white">{data.wallet.network_name}</p>
                </div>
              </div>
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-gray-400 font-medium mb-2">Owner</p>
                  <p className="text-base font-semibold text-white">{data.wallet.owner_name || '-'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-400 font-medium mb-2">Label</p>
                  <p className="text-base font-semibold text-white">{data.wallet.label}</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Transactions Card */}
        <Card className="backdrop-blur-xl bg-gray-900/70 border-gray-700/50 shadow-2xl">
          <CardHeader>
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
              <div>
                <CardTitle className="text-2xl font-bold text-white">Transaksi Terbaru</CardTitle>
                <CardDescription className="text-gray-400">
                    Menampilkan {data.transactions.items.length > 0 ? ((currentPage - 1) * pageSize) + 1 : 0} - {Math.min(currentPage * pageSize, data.transactions.total)} dari {data.transactions.total} transaksi
                </CardDescription>
              </div>
              <div className="w-full md:w-72 relative">
                <Input
                  type="text"
                  placeholder="Cari Tx Hash..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 bg-gray-800/50 border-gray-700 text-white placeholder:text-gray-500 focus:ring-purple-500 focus:border-purple-500"
                />
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto mb-6">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-700">
                    <th className="text-left py-4 px-4 text-sm font-semibold text-gray-300">Tx Hash</th>
                    <th className="text-left py-4 px-4 text-sm font-semibold text-gray-300">From → To</th>
                    <th className="text-right py-4 px-4 text-sm font-semibold text-gray-300">Time</th>
                    <th className="text-center py-4 px-4 text-sm font-semibold text-gray-300">Direction</th>
                    <th className="text-center py-4 px-4 text-sm font-semibold text-gray-300">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredTransactions.length > 0 ? (
                    filteredTransactions.map((tx) => (
                    <tr key={tx.tx_hash} className="border-b border-gray-800 hover:bg-gray-800/50 transition-colors">
                      <td className="py-4 px-4">
                        <div className="flex items-center gap-2">
                          <code className="text-xs text-gray-400 font-mono break-all">
                            {tx.tx_hash}
                          </code>
                          <Button 
                            size="sm" 
                            variant="ghost"
                            onClick={() => copyToClipboard(tx.tx_hash)}
                            className="h-6 w-6 p-0 text-gray-500 hover:text-white hover:bg-transparent"
                          >
                            <Copy className="w-3 h-3" />
                          </Button>
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <code className="text-xs text-gray-400 font-mono break-all">
                              {tx.from_address}
                            </code>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-gray-500">→</span>
                            <code className="text-xs text-gray-400 font-mono break-all">
                              {tx.to_address ? tx.to_address : '-'}
                            </code>
                          </div>
                        </div>
                      </td>
                      <td className="py-4 px-4 text-right text-sm text-gray-400">{new Date(tx.time_stamp).toLocaleString()}</td>
                      <td className="py-4 px-4 text-center">
                        <Badge 
                          variant="outline" 
                          className={`${
                            tx.direction === "out" 
                              ? "border-red-500/30 bg-red-500/10 text-red-400" 
                              : tx.direction === "in"
                              ? "border-green-500/30 bg-green-500/10 text-green-400"
                              : "border-gray-500/30 bg-gray-500/10 text-gray-400"
                          }`}
                        >
                          {tx.direction.toUpperCase()}
                        </Badge>
                      </td>
                      <td className="py-4 px-4 text-center">
                        <Badge variant="outline" className="border-green-500/30 text-green-400">
                           {tx.status}
                        </Badge>
                      </td>
                    </tr>
                  ))
                  ) : (
                    <tr>
                      <td colSpan={5} className="py-8 text-center text-gray-400">
                        Tidak ada transaksi yang ditemukan
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination Controls */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2">
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="h-9 w-9 bg-gray-800/50 border-gray-700 text-gray-300 hover:text-white hover:bg-gray-700"
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>

                <div className="flex items-center gap-1">
                 {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    let pageNum;
                    if (totalPages <= 5) {
                        pageNum = i + 1;
                    } else if (currentPage <= 3) {
                        pageNum = i + 1;
                    } else if (currentPage >= totalPages - 2) {
                        pageNum = totalPages - 4 + i;
                    } else {
                        pageNum = currentPage - 2 + i;
                    }
                    
                    return (
                        <Button
                            key={pageNum}
                            variant={currentPage === pageNum ? "default" : "outline"}
                            size="sm"
                            onClick={() => setCurrentPage(pageNum)}
                            className={`h-9 min-w-[36px] px-3 ${
                                currentPage === pageNum 
                                    ? "bg-gradient-to-r from-purple-600 to-fuchsia-600 hover:from-purple-700 hover:to-fuchsia-700 text-white border-0" 
                                    : "bg-gray-800/50 border-gray-700 text-gray-300 hover:text-white hover:bg-gray-700"
                            }`}
                        >
                            {pageNum}
                        </Button>
                    );
                })}
                </div>

                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className="h-9 w-9 bg-gray-800/50 border-gray-700 text-gray-300 hover:text-white hover:bg-gray-700"
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default WalletDetail;
