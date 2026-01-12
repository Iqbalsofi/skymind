'use client'

import { useState } from 'react'
import SearchForm from '@/components/SearchForm'
import FlightResults from '@/components/FlightResults'

export default function Home() {
    const [results, setResults] = useState(null)
    const [loading, setLoading] = useState(false)

    const handleSearch = async (searchData: any) => {
        setLoading(true)
        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/search`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(searchData),
            })
            const data = await response.json()
            setResults(data)
        } catch (error) {
            console.error('Search error:', error)
        } finally {
            setLoading(false)
        }
    }

    return (
        <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
            {/* Header */}
            <header className="bg-white dark:bg-gray-800 shadow-sm">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                                SkyMind ✈️
                            </h1>
                            <p className="text-sm text-gray-600 dark:text-gray-300">
                                Skyscanner shows flights. We ship decisions.
                            </p>
                        </div>
                        <div className="flex gap-4">
                            <a
                                href={`${process.env.NEXT_PUBLIC_API_URL}/docs`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400"
                            >
                                API Docs
                            </a>
                            <a
                                href="https://github.com/Iqbalsofi/skymind"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-sm text-gray-600 hover:text-gray-900 dark:text-gray-300"
                            >
                                GitHub
                            </a>
                        </div>
                    </div>
                </div>
            </header>

            {/* Hero Section */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                <div className="text-center mb-12">
                    <h2 className="text-5xl font-extrabold text-gray-900 dark:text-white mb-4">
                        Find Your Perfect Flight
                    </h2>
                    <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
                        Powered by AI-driven ranking, risk detection, and transparent explanations
                    </p>
                </div>

                {/* Search Form */}
                <SearchForm onSearch={handleSearch} loading={loading} />

                {/* Results */}
                {results && <FlightResults results={results} />}

                {/* Loading State */}
                {loading && (
                    <div className="text-center py-12">
                        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
                        <p className="mt-4 text-gray-600 dark:text-gray-300">Searching for the best flights...</p>
                    </div>
                )}
            </div>

            {/* Footer */}
            <footer className="bg-white dark:bg-gray-800 mt-20">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                    <div className="text-center text-gray-600 dark:text-gray-300">
                        <p>Built with ❤️ using Next.js & FastAPI</p>
                        <p className="text-sm mt-2">© 2026 SkyMind. All rights reserved.</p>
                    </div>
                </div>
            </footer>
        </main>
    )
}
