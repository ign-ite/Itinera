import React, { useState, useEffect } from "react";
import { motion, useAnimation } from "framer-motion";
import {
  Sun,
  Moon,
  Search,
  Menu,
  Loader2,
  MapPin,
  Calendar,
  Users,
  Wallet,
  Send,
  CheckCircle,
  XCircle,
} from "lucide-react";

export default function App() {
  const [dark, setDark] = useState(false);
  const [query, setQuery] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [loadingScreen, setLoadingScreen] = useState(true);

  // API states
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const controls = useAnimation();

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
  }, [dark]);

  useEffect(() => {
    const timer = setTimeout(() => setLoadingScreen(false), 1500);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    const tags = [
      "temples",
      "beach",
      "mountains",
      "food",
      "culture",
      "adventure",
      "city-break",
      "romantic",
      "budget",
    ];

    if (!query.trim()) {
      setSuggestions([
        "Plan a 5-day temple tour from Chennai under 30k for 2 people",
        "I want a beach vacation from Mumbai for 7 days, budget 50k",
        "Weekend getaway from Bangalore for family of 4, 20k budget",
      ]);
      return;
    }

    const q = query.toLowerCase();
    setSuggestions(tags.filter((t) => t.includes(q)).slice(0, 6));
  }, [query]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch("http://localhost:8000/plan/sync", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: query }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to generate plan");
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loadingScreen) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-b from-purple-800 to-indigo-900 text-white text-xl font-bold">
        Loading Itinera...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-100 to-white dark:from-gray-900 dark:to-black transition-colors duration-500">
      {/* Header */}
      <header className="max-w-6xl mx-auto px-6 py-6 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="text-2xl font-bold text-gray-800 dark:text-gray-100">
            Itinera<span className="text-amber-500">.</span>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <button
            onClick={() => setDark((s) => !s)}
            className="p-2 rounded-lg bg-white/60 dark:bg-black/40 backdrop-blur text-gray-800 dark:text-gray-100"
            aria-label="Toggle dark mode"
          >
            {dark ? <Sun size={18} /> : <Moon size={18} />}
          </button>

          {/* Removed Get the app button */}
          <button className="md:hidden p-2 rounded-md bg-white/60 dark:bg-black/40">
            <Menu size={18} />
          </button>
        </div>
      </header>

      {/* Hero */}
      <main className="max-w-6xl mx-auto px-6">
        <section className="relative rounded-2xl overflow-hidden bg-gradient-to-r from-purple-800 to-indigo-900 h-[100vh] shadow-lg flex flex-col items-center justify-center text-center px-6">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1 }}
            className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1500&q=80')] bg-cover bg-center opacity-40"
          />

          <motion.h1
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="relative z-10 text-4xl md:text-5xl font-extrabold text-brown drop-shadow-lg"
          >
            Plan Your Perfect Journey
          </motion.h1>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.15 }}
            className="relative z-10 text-brown/90 max-w-2xl mt-4"
          >
            Describe your dream trip in natural language. AI-powered planning with budget validation and complete itineraries.
          </motion.p>

          {/* Input Section */}
          <motion.form
            onSubmit={handleSubmit}
            initial={{ scale: 0.98, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.25 }}
            className="relative z-10 mt-6 bg-white/90 dark:bg-gray-900/80 rounded-xl p-4 shadow-md w-full max-w-3xl backdrop-blur-md"
          >
            <div className="flex gap-2 items-start">
              <Search size={18} className="text-gray-600 dark:text-gray-300 mt-2" />
              <textarea
                className="flex-1 bg-transparent outline-none text-gray-800 dark:text-gray-100 resize-none min-h-[100px]"
                placeholder="Tell me about your trip..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading || !query.trim()}
                className="flex items-center gap-2 px-4 py-2 bg-amber-500 text-white rounded-lg hover:bg-amber-600 transition-colors disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    Generate Plan
                  </>
                )}
              </button>
            </div>

            {/* Suggestions */}
            <div className="mt-4 flex flex-wrap gap-2">
              {suggestions.map((s, i) => (
                <button
                  key={i}
                  onClick={() => setQuery(s)}
                  className="px-3 py-1 rounded-full bg-gray-100 dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-200 hover:bg-amber-100 dark:hover:bg-amber-600 transition-colors"
                >
                  {s}
                </button>
              ))}
            </div>
          </motion.form>
        </section>

        {/* Results Section */}
        {(loading || result || error) && (
          <section className="mt-10 space-y-6">
            {loading && (
              <div className="bg-white/10 dark:bg-gray-800/60 rounded-2xl p-12 text-center border border-white/20">
                <Loader2 className="w-16 h-16 animate-spin text-amber-400 mx-auto mb-4" />
                <p className="text-white text-xl">Creating your personalized itinerary...</p>
                <p className="text-gray-400 mt-2">This may take 30-60 seconds</p>
              </div>
            )}

            {error && (
              <div className="bg-red-500/10 rounded-2xl p-8 border border-red-500/30">
                <div className="flex items-center gap-3 mb-2">
                  <XCircle className="w-6 h-6 text-red-400" />
                  <h3 className="text-xl font-semibold text-red-400">Error</h3>
                </div>
                <p className="text-gray-300">{error}</p>
              </div>
            )}

            {result && (
              <div className="space-y-6">
                {/* Status */}
                <div
                  className={`${
                    result.within_budget
                      ? "bg-green-500/10 border-green-500/30"
                      : "bg-yellow-500/10 border-yellow-500/30"
                  } rounded-2xl p-6 border`}
                >
                  <div className="flex items-center gap-3">
                    <CheckCircle
                      className={`w-8 h-8 ${
                        result.within_budget ? "text-green-400" : "text-yellow-400"
                      }`}
                    />
                    <div>
                      <h3 className="text-2xl font-bold text-white">
                        {result.destination}
                      </h3>
                      <p
                        className={`text-lg ${
                          result.within_budget ? "text-green-300" : "text-yellow-300"
                        }`}
                      >
                        Total: ₹{result.total_cost?.toLocaleString()} / ₹
                        {result.budget_limit?.toLocaleString()}{" "}
                        {result.within_budget ? "✓ Within Budget" : "⚠ Over Budget"}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Quick Stats */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <StatCard icon={<MapPin />} label="Destination" value={result.destination} />
                  <StatCard icon={<Calendar />} label="Duration" value={`${result.plan_data?.metadata?.trip_duration} days`} />
                  <StatCard icon={<Users />} label="Travelers" value={result.plan_data?.metadata?.travelers} />
                  <StatCard icon={<Wallet />} label="Budget" value={`₹${result.budget_limit?.toLocaleString()}`} />
                </div>

                {/* Itinerary */}
                <div className="bg-white/10 dark:bg-gray-800/40 rounded-2xl p-8 border border-white/20">
                  <h2 className="text-2xl font-bold text-white mb-6">Complete Itinerary</h2>
                  {result.plan_data?.itinerary?.itinerary?.map((day, idx) => (
                    <div key={idx} className="mb-6">
                      <h3 className="text-xl font-semibold text-amber-300 mb-3">Day {day.day}</h3>
                      <div className="space-y-3">
                        {day.activities?.map((activity, actIdx) => (
                          <div
                            key={actIdx}
                            className="bg-white/5 rounded-lg p-4 border border-white/10"
                          >
                            <div className="flex justify-between items-start mb-2">
                              <h4 className="text-white font-medium">{activity.activity}</h4>
                              <span className="text-amber-300 text-sm">{activity.time}</span>
                            </div>
                            <p className="text-gray-400 text-sm mb-1">{activity.location}</p>
                            <p className="text-gray-300 text-sm">{activity.description}</p>
                            {activity.transportation && (
                              <p className="text-blue-300 text-sm mt-2">
                                🚗 {activity.transportation}
                              </p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}

                  {/* Budget Breakdown */}
                  {result.plan_data?.budget?.validation && (
                    <div className="mt-8 pt-8 border-t border-white/20">
                      <h3 className="text-xl font-bold text-white mb-4">Budget Breakdown</h3>
                      <div className="space-y-2">
                        {Object.entries(
                          result.plan_data.budget.validation.categories || {}
                        ).map(
                          ([category, items]) =>
                            Array.isArray(items) &&
                            items.length > 0 && (
                              <div
                                key={category}
                                className="flex justify-between text-gray-300"
                              >
                                <span className="capitalize">{category}:</span>
                                <span className="text-white font-semibold">
                                  ₹
                                  {items
                                    .reduce((sum, item) => sum + (item.cost || 0), 0)
                                    .toLocaleString()}
                                </span>
                              </div>
                            )
                        )}
                        <div className="flex justify-between text-lg font-bold text-white pt-3 border-t border-white/20">
                          <span>Total:</span>
                          <span>₹{result.total_cost?.toLocaleString()}</span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Recommendations */}
                  {result.plan_data?.recommendations?.length > 0 && (
                    <div className="mt-6 p-4 bg-blue-500/10 rounded-lg border border-blue-500/30">
                      <h4 className="text-blue-300 font-semibold mb-2">Recommendations:</h4>
                      <ul className="text-gray-300 text-sm space-y-1">
                        {result.plan_data.recommendations.map((rec, idx) => (
                          <li key={idx}>• {rec}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}
          </section>
        )}

        {/* Features */}
        <section className="mt-10 grid grid-cols-1 md:grid-cols-3 gap-6">
          <FeatureCard
            title="See it all"
            body="From local trips to global adventures, discover endless travel possibilities."
          />
          <FeatureCard
            title="Compare right here"
            body="No need to search everywhere. The largest travel ideas in one place."
          />
          <FeatureCard
            title="Get exclusive plans"
            body="We craft and optimize itineraries so you get the most value for your budget."
          />
        </section>

        {/* Footer */}
        <footer className="mt-12 py-10 text-gray-600 dark:text-gray-300">
          <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
            © {new Date().getFullYear()} Itinera
          </div>
        </footer>
      </main>
    </div>
  );
}

function FeatureCard({ title, body }) {
  return (
    <motion.div
      className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-sm hover:shadow-lg transition-shadow"
      initial={{ opacity: 0, y: 10 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
    >
      <h3 className="font-semibold text-gray-800 dark:text-gray-100">{title}</h3>
      <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">{body}</p>
    </motion.div>
  );
}

function StatCard({ icon, label, value }) {
  return (
    <div className="bg-white/10 dark:bg-gray-800/40 rounded-xl p-4 border border-white/20">
      <div className="mb-2">{icon}</div>
      <p className="text-gray-400 text-sm">{label}</p>
      <p className="text-white font-semibold">{value}</p>
    </div>
  );
}
