private long _cacheHits = 0;
private long _cacheMisses = 0;

public (long Hits, long Misses) GetCacheStats() => (_cacheHits, _cacheMisses);

// In RetrieveHyperCognitiveContext():
System.Threading.Interlocked.Increment(ref _cacheMisses);  // Thread-safe
System.Threading.Interlocked.Increment(ref _cacheHits);    // Thread-safe