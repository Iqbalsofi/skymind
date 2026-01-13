'use client'

import { useState } from 'react'

interface FlightCardProps {
    itinerary: any
    rank: number
}

export default function FlightCard({ itinerary, rank }: FlightCardProps) {
    const [expanded, setExpanded] = useState(false)

    const getRankBadgeColor = (rank: number) => {
        if (rank === 1) return 'bg-yellow-400 text-yellow-900'
        if (rank === 2) return 'bg-gray-300 text-gray-900'
        if (rank === 3) return 'bg-orange-400 text-orange-900'
        return 'bg-blue-100 text-blue-900'
    }

    const formatDuration = (minutes: number) => {
        const hours = Math.floor(minutes / 60)
        const mins = minutes % 60
        return `${hours}h ${mins}m`
    }

    const formatTime = (dateString: string) => {
        return new Date(dateString).toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
        })
    }

    return (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg hover:shadow-xl transition-all overflow-hidden border border-gray-200 dark:border-gray-700">
            {/* Main Card Content */}
            <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                    {/* Rank Badge */}
                    <div className={`px-3 py-1 rounded-full text-sm font-bold ${getRankBadgeColor(rank)}`}>
                        #{rank}
                    </div>

                    {/* Score */}
                    <div className="text-right">
                        <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                            {itinerary.score?.toFixed(1) || 'N/A'}
                        </div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">Score</div>
                    </div>
                </div>

                {/* Flight Route */}
                <div className="grid grid-cols-3 gap-4 items-center mb-4">
                    {/* Departure */}
                    <div>
                        <div className="text-2xl font-bold text-gray-900 dark:text-white">
                            {itinerary.legs[0].departure_time && formatTime(itinerary.legs[0].departure_time)}
                        </div>
                        <div className="text-sm text-gray-600 dark:text-gray-300">
                            {itinerary.legs[0].origin_code}
                        </div>
                    </div>

                    {/* Duration & Stops */}
                    <div className="text-center">
                        <div className="text-sm text-gray-600 dark:text-gray-300 mb-1">
                            {formatDuration(itinerary.total_duration_minutes)}
                        </div>
                        <div className="h-1 bg-gray-300 dark:bg-gray-600 rounded relative">
                            <div className="absolute left-0 top-1/2 -translate-y-1/2 w-2 h-2 bg-blue-600 rounded-full"></div>
                            <div className="absolute right-0 top-1/2 -translate-y-1/2 w-2 h-2 bg-blue-600 rounded-full"></div>
                        </div>
                        <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            {itinerary.num_stops === 0 ? 'Direct' : `${itinerary.num_stops} stop${itinerary.num_stops > 1 ? 's' : ''}`}
                        </div>
                    </div>

                    {/* Arrival */}
                    <div className="text-right">
                        <div className="text-2xl font-bold text-gray-900 dark:text-white">
                            {itinerary.legs[itinerary.legs.length - 1].arrival_time &&
                                formatTime(itinerary.legs[itinerary.legs.length - 1].arrival_time)}
                        </div>
                        <div className="text-sm text-gray-600 dark:text-gray-300">
                            {itinerary.legs[itinerary.legs.length - 1].destination_code}
                        </div>
                    </div>
                </div>

                {/* Price & Actions */}
                <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
                    <div>
                        {/* Price Analysis Badge (Phase 3) */}
                        {itinerary.price_analysis && (
                            <div className={`mb-2 px-2 py-1 rounded inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider ${itinerary.price_analysis.advice === 'buy_now'
                                    ? 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300'
                                    : itinerary.price_analysis.advice === 'wait'
                                        ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300'
                                        : 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300'
                                }`}>
                                <span>
                                    {itinerary.price_analysis.advice === 'buy_now' ? '⚡ Buy Now' :
                                        itinerary.price_analysis.advice === 'wait' ? '⏳ Wait' : '👀 Monitor'}
                                </span>
                            </div>
                        )}
                        <div className="text-3xl font-bold text-gray-900 dark:text-white">
                            ${itinerary.price?.total_usd?.toFixed(2) || '0.00'}
                        </div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                            {itinerary.price.currency} • {itinerary.price_analysis?.factors?.[0] || 'Market Price'}
                        </div>
                    </div>

                    <div className="flex gap-3">
                        <button
                            onClick={() => setExpanded(!expanded)}
                            className="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-all"
                        >
                            {expanded ? 'Hide Details' : 'Show Details'}
                        </button>
                        <button className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-md hover:shadow-lg transition-all">
                            Book Now
                        </button>
                    </div>
                </div>

                {/* Risk Flags */}
                {itinerary.risk_flags && itinerary.risk_flags.length > 0 && (
                    <div className="mt-4 flex flex-wrap gap-2">
                        {itinerary.risk_flags.map((risk: any, idx: number) => (
                            <span
                                key={idx}
                                className="px-3 py-1 bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300 text-xs rounded-full"
                            >
                                ⚠️ {risk.risk_type.replace('_', ' ')}
                            </span>
                        ))}
                    </div>
                )}
            </div>

            {/* Expanded Details */}
            {expanded && (
                <div className="border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50 p-6 space-y-4">
                    {/* Score Breakdown */}
                    {itinerary.score_breakdown && (
                        <div>
                            <h4 className="font-semibold text-gray-900 dark:text-white mb-3">Score Breakdown</h4>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                                {Object.entries(itinerary.score_breakdown).map(([key, value]: [string, any]) => (
                                    <div key={key} className="bg-white dark:bg-gray-800 p-3 rounded-lg">
                                        <div className="text-xs text-gray-600 dark:text-gray-400 capitalize">
                                            {key.replace('_', ' ')}
                                        </div>
                                        <div className="text-lg font-bold text-blue-600 dark:text-blue-400">
                                            {value.toFixed(1)}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Explanation */}
                    {itinerary.explanation && (
                        <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                            <h4 className="font-semibold text-blue-900 dark:text-blue-300 mb-2">Why this ranking?</h4>
                            <p className="text-sm text-blue-800 dark:text-blue-200">{itinerary.explanation}</p>
                        </div>
                    )}

                    {/* Airline Info */}
                    <div>
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Airlines</h4>
                        <div className="flex flex-wrap gap-2">
                            {itinerary.legs.map((leg: any, idx: number) => (
                                <span key={idx} className="px-3 py-1 bg-white dark:bg-gray-800 rounded-lg text-sm">
                                    {leg.airline_name} ({leg.airline_code})
                                </span>
                            ))}
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
