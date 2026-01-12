import { useState, useRef, useEffect } from 'react'
import { airports } from '../data/airports'

interface AirportInputProps {
    label: string
    value: string
    onChange: (value: string) => void
    placeholder: string
}

export default function AirportInput({ label, value, onChange, placeholder }: AirportInputProps) {
    const [query, setQuery] = useState(value)
    const [isOpen, setIsOpen] = useState(false)
    const wrapperRef = useRef<HTMLDivElement>(null)

    // Filter airports
    const filtered = query === ''
        ? []
        : airports.filter((airport) => {
            return airport.city.toLowerCase().includes(query.toLowerCase()) ||
                airport.code.toLowerCase().includes(query.toLowerCase()) ||
                airport.name.toLowerCase().includes(query.toLowerCase())
        }).slice(0, 5)

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
                setIsOpen(false)
            }
        }
        document.addEventListener('mousedown', handleClickOutside)
        return () => document.removeEventListener('mousedown', handleClickOutside)
    }, [])

    // Update query when value prop changes (e.g. initial load)
    useEffect(() => {
        // If query doesn't match value (and we aren't typing), sync them.
        // But since we control query locally for typing, we just initialize.
        // Actually, we should sync if value changes externally.
        if (value && !query) setQuery(value);
    }, [value])

    return (
        <div className="relative" ref={wrapperRef}>
            <label className="block text-xs font-semibold text-gray-500 dark:text-gray-400 mb-1 uppercase tracking-wider">
                {label}
            </label>
            <input
                type="text"
                value={query}
                onChange={(e) => {
                    setQuery(e.target.value)
                    setIsOpen(true)
                    if (e.target.value === '') onChange('')
                }}
                onFocus={() => setIsOpen(true)}
                className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-800/50 border-0 rounded-xl focus:ring-2 focus:ring-blue-500 text-lg font-medium text-gray-900 dark:text-white placeholder-gray-400 transition-all font-sans"
                placeholder={placeholder}
            />

            {isOpen && filtered.length > 0 && (
                <div className="absolute z-50 w-full mt-1 bg-white dark:bg-gray-800 rounded-xl shadow-2xl border border-gray-100 dark:border-gray-700 overflow-hidden">
                    {filtered.map((airport) => (
                        <div
                            key={airport.code}
                            onClick={() => {
                                setQuery(`${airport.city} (${airport.code})`)
                                onChange(airport.code)
                                setIsOpen(false)
                            }}
                            className="px-4 py-3 hover:bg-blue-50 dark:hover:bg-gray-700 cursor-pointer transition-colors border-b border-gray-100 dark:border-gray-700 last:border-0"
                        >
                            <div className="flex justify-between items-center">
                                <span className="font-bold text-gray-900 dark:text-white">{airport.city}</span>
                                <span className="text-sm font-mono bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-300 px-2 py-0.5 rounded font-bold">{airport.code}</span>
                            </div>
                            <div className="text-xs text-gray-500 dark:text-gray-400 truncate">{airport.name}</div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}
