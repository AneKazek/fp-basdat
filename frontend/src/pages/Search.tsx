import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const isValidAddress = (addr: string) => /^0x[a-fA-F0-9]{40}$/.test(addr);

const Search: React.FC = () => {
  const navigate = useNavigate();
  const [address, setAddress] = useState('');
  const [error, setError] = useState('');

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const addr = address.trim();
    if (!isValidAddress(addr)) {
      setError('Alamat harus 0x dan 42 karakter');
      return;
    }
    setError('');
    navigate(`/wallet/${addr.toLowerCase()}`);
  };

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="max-w-xl w-full bg-white border rounded-xl p-6">
        <h1 className="text-2xl font-bold mb-4">Ethereum Wallet Tracker</h1>
        <form onSubmit={onSubmit} className="space-y-3">
          <label className="block text-sm text-gray-600">Masukkan alamat Ethereum (0x...)</label>
          <input
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            placeholder="0x..."
            className="w-full border rounded px-3 py-2"
          />
          {error && <p className="text-red-600 text-sm">{error}</p>}
          <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded">Search</button>
        </form>
      </div>
    </div>
  );
};

export default Search;

