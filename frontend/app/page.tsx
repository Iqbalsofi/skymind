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
            <header className="bg-white/50 dark:bg-gray-900/50 backdrop-blur-md sticky top-0 z-50 border-b border-gray-200/50 dark:border-gray-800/50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <span className="text-2xl pt-1">✈️</span>
                            <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-400 dark:to-indigo-400">
                                SkyMind
                            </h1>
                        </div>
                        <div className="flex gap-6">
                            <a
                                href={`${process.env.NEXT_PUBLIC_API_URL}/docs`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-sm font-medium text-gray-600 hover:text-blue-600 dark:text-gray-300 dark:hover:text-blue-400 transition-colors"
                            >
                                API Docs
                            </a>
                            <a
                                href="https://github.com/Iqbalsofi/skymind"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-sm font-medium text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white transition-colors"
                            >
                                GitHub
                            </a>
                        </div>
                    </div>
                </div>
            </header>

            {/* Hero Section */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
                <div className="text-center mb-16 space-y-4">
                    <h2 className="text-5xl md:text-7xl font-extrabold text-gray-900 dark:text-white tracking-tight">
                        Travel Smarter.
                    </h2>
                    <p className="text-xl text-gray-500 dark:text-gray-400 max-w-2xl mx-auto font-light">
                        AI-powered flight decisions, not just search results.
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
