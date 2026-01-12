'use client'

import { useState } from 'react'

interface SearchFormProps {
    onSearch: (data: any) => void
    loading: boolean
}

export default function SearchForm({ onSearch, loading }: SearchFormProps) {
    const [formData, setFormData] = useState({
        origins: ['JFK'],
        destinations: ['LAX'],
        departure_date: new Date().toISOString().split('T')[0],
        cabin_class: 'economy',
        priority: 'balanced',
    })

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        onSearch({
            ...formData,
            max_stops: null,
            nonstop_only: false,
            max_price_usd: null,
        })
    }

    return (
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 mb-12">
            <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
                {/* Origin */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        From
                    </label>
                    <input
                        type="text"
                        value={formData.origins[0]}
                        onChange={(e) => setFormData({ ...formData, origins: [e.target.value] })}
                        className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                        placeholder="JFK"
                    />
                </div>

                {/* Destination */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        To
                    </label>
                    <input
                        type="text"
                        value={formData.destinations[0]}
                        onChange={(e) => setFormData({ ...formData, destinations: [e.target.value] })}
                        className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                        placeholder="LAX"
                    />
                </div>

                {/* Date */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Departure
                    </label>
                    <input
                        type="date"
                        value={formData.departure_date}
                        onChange={(e) => setFormData({ ...formData, departure_date: e.target.value })}
                        className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    />
                </div>

                {/* Cabin Class */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Class
                    </label>
                    <select
                        value={formData.cabin_class}
                        onChange={(e) => setFormData({ ...formData, cabin_class: e.target.value })}
                        className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    >
                        <option value="economy">Economy</option>
                        <option value="premium_economy">Premium Economy</option>
                        <option value="business">Business</option>
                        <option value="first">First Class</option>
                    </select>
                </div>

                {/* Search Button */}
                <div className="flex items-end">
                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-md hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {loading ? 'Searching...' : 'Search Flights'}
                    </button>
                </div>
            </form>

            {/* Priority Toggle */}
            <div className="mt-6 flex items-center justify-center gap-4">
                <span className="text-sm text-gray-600 dark:text-gray-300">Priority:</span>
                {['cheapest', 'balanced', 'fastest'].map((priority) => (
                    <button
                        key={priority}
                        type="button"
                        onClick={() => setFormData({ ...formData, priority })}
                        className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${formData.priority === priority
                                ? 'bg-blue-600 text-white shadow-lg'
                                : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                            }`}
                    >
                        {priority.charAt(0).toUpperCase() + priority.slice(1)}
                    </button>
                ))}
            </div>
        </div>
    )
}
