'use client'

import FlightCard from './FlightCard'

interface FlightResultsProps {
    results: any
}

export default function FlightResults({ results }: FlightResultsProps) {
    if (!results?.itineraries || results.itineraries.length === 0) {
        return (
            <div className="text-center py-12">
                <p className="text-gray-600 dark:text-gray-300">No flights found. Try adjusting your search.</p>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            {/* Results Header */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                    Found {results.total_results} flights
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-300">
                    Ranked by intelligent scoring • Search time: {results.search_time_ms}ms
                </p>
            </div>

            {/* Flight Cards */}
            <div className="grid gap-6">
                {results.itineraries.map((itinerary: any, index: number) => (
                    <FlightCard
                        key={itinerary.itinerary_id}
                        itinerary={itinerary}
                        rank={index + 1}
                    />
                ))}
            </div>
        </div>
    )
}
