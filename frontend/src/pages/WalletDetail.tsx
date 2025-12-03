import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import api from '../services/api';

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
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [error, setError] = useState('');

  const fetchData = async (p = 1) => {
    try {
      const res = await api.get<WalletInfoResp>(`/wallet/${address}`, { params: { page: p, pageSize } });
      setData(res.data);
      setError('');
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Terjadi kesalahan');
    }
  };

  useEffect(() => {
    setPage(1);
    fetchData(1);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [address]);

  const nextPage = () => {
    const maxPage = data ? Math.ceil(data.transactions.total / pageSize) : 1;
    if (page < maxPage) {
      const newPage = page + 1;
      setPage(newPage);
      fetchData(newPage);
    }
  };

  const prevPage = () => {
    if (page > 1) {
      const newPage = page - 1;
      setPage(newPage);
      fetchData(newPage);
    }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="mb-4">
        <Link to="/" className="text-blue-600">&larr; Back to search</Link>
      </div>

      {error && (
        <div className="border rounded bg-red-50 text-red-700 p-4 mb-4">
          {error}
        </div>
      )}

      {data && (
        <div className="space-y-6">
          <div className="border rounded p-4 bg-white">
            <h2 className="text-xl font-bold mb-2">Wallet Summary</h2>
            <p><strong>Address:</strong> {data.wallet.address}</p>
            <p><strong>Network:</strong> {data.wallet.network_name}</p>
            {data.wallet.owner_name && <p><strong>Owner:</strong> {data.wallet.owner_name}</p>}
            <p><strong>Label:</strong> {data.wallet.label}</p>
          </div>

          <div className="border rounded p-4 bg-white">
            <h3 className="text-lg font-semibold mb-3">Latest Transactions</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-gray-100 text-left">
                    <th className="px-3 py-2">Tx Hash</th>
                    <th className="px-3 py-2">From → To</th>
                    <th className="px-3 py-2">Value (ETH)</th>
                    <th className="px-3 py-2">Fee (ETH)</th>
                    <th className="px-3 py-2">Time</th>
                    <th className="px-3 py-2">Direction</th>
                    <th className="px-3 py-2">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {data.transactions.items.map((tx) => (
                    <tr key={tx.tx_hash} className="border-t">
                      <td className="px-3 py-2 font-mono">{tx.tx_hash}</td>
                      <td className="px-3 py-2">
                        <span className={tx.from_address.toLowerCase() === data.wallet.address.toLowerCase() ? 'font-bold' : ''}>{tx.from_address}</span>
                        {' '}→{' '}
                        <span className={tx.to_address?.toLowerCase() === data.wallet.address.toLowerCase() ? 'font-bold' : ''}>{tx.to_address || '-'}</span>
                      </td>
                      <td className="px-3 py-2">{Number(tx.value_eth).toFixed(6)}</td>
                      <td className="px-3 py-2">{Number(tx.tx_fee_eth).toFixed(6)}</td>
                      <td className="px-3 py-2">{new Date(tx.time_stamp).toLocaleString()}</td>
                      <td className="px-3 py-2">
                        {tx.direction === 'in' ? (
                          <span className="text-green-600">In</span>
                        ) : tx.direction === 'out' ? (
                          <span className="text-red-600">Out</span>
                        ) : (
                          <span className="text-gray-600">Self</span>
                        )}
                      </td>
                      <td className="px-3 py-2">{tx.status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="flex items-center justify-between mt-3">
              <button onClick={prevPage} className="px-3 py-1 border rounded" disabled={page === 1}>Prev</button>
              <div>Page {page} of {Math.max(1, Math.ceil(data.transactions.total / pageSize))}</div>
              <button onClick={nextPage} className="px-3 py-1 border rounded" disabled={page >= Math.ceil(data.transactions.total / pageSize)}>Next</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WalletDetail;

