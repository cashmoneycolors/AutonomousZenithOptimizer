using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Threading;
using System.Threading.Tasks;
using StackExchangeRedis = StackExchange.Redis;
using ZenithCoreSystem;

namespace ZenithCoreSystem.Modules
{
    public interface IConnectionMultiplexer
    {
        IDatabase GetDatabase(int db);
    }

    public interface IDatabase
    {
        Task<RedisValue> StringGetAsync(string key);
        Task<bool> StringSetAsync(string key, string value, TimeSpan expiry);
    }

    public class RedisValue
    {
        public static RedisValue Null { get; } = new RedisValue();
        public bool IsNull { get; set; } = true;
        public string? Value { get; set; }

        public static implicit operator RedisValue(string? value) => new RedisValue
        {
            IsNull = value == null,
            Value = value
        };

        public override string ToString() => Value ?? "NULL";
    }

    public class RedisMock : IConnectionMultiplexer
    {
        private readonly Dictionary<string, string> _storage = new();

        public IDatabase GetDatabase(int db) => new RedisDbMock(_storage);
    }

    public class RedisDbMock : IDatabase
    {
        private readonly Dictionary<string, string> _storage;

        public RedisDbMock(Dictionary<string, string> storage)
        {
            _storage = storage;
        }

        public Task<RedisValue> StringGetAsync(string key)
        {
            return Task.FromResult(_storage.ContainsKey(key)
                ? new RedisValue { IsNull = false, Value = _storage[key] }
                : RedisValue.Null);
        }

        public Task<bool> StringSetAsync(string key, string value, TimeSpan expiry)
        {
            _storage[key] = value;
            return Task.FromResult(true);
        }
    }

    public sealed class StackExchangeRedisConnection : IConnectionMultiplexer, IDisposable
    {
        private readonly StackExchangeRedis.ConnectionMultiplexer _multiplexer;

        public StackExchangeRedisConnection(StackExchangeRedis.ConnectionMultiplexer multiplexer)
        {
            _multiplexer = multiplexer;
        }

        public IDatabase GetDatabase(int db)
        {
            return new StackExchangeRedisDatabase(_multiplexer.GetDatabase(db));
        }

        public void Dispose()
        {
            _multiplexer.Dispose();
        }
    }

    public sealed class StackExchangeRedisDatabase : IDatabase
    {
        private readonly StackExchangeRedis.IDatabase _database;

        public StackExchangeRedisDatabase(StackExchangeRedis.IDatabase database)
        {
            _database = database;
        }

        public async Task<RedisValue> StringGetAsync(string key)
        {
            StackExchangeRedis.RedisValue value = await _database.StringGetAsync(key).ConfigureAwait(false);
            return value.HasValue
                ? new RedisValue { IsNull = false, Value = value.ToString() }
                : RedisValue.Null;
        }

        public Task<bool> StringSetAsync(string key, string value, TimeSpan expiry)
        {
            return _database.StringSetAsync(key, value, expiry);
        }
    }

    public class HoloKognitivesRepository : IHyperCache
    {
        private readonly IDatabase _db;
        private long _cacheHits = 0;
        private long _cacheMisses = 0;
        private double _lastRetrieveLatencyMs = 0;

        public HoloKognitivesRepository(IConnectionMultiplexer redis)
        {
            _db = redis.GetDatabase(0);
        }

        public (long Hits, long Misses) GetCacheStats() => (_cacheHits, _cacheMisses);
        public void ResetCacheStats() { _cacheHits = 0; _cacheMisses = 0; }

        public double GetLastRetrieveLatencyMs() => Volatile.Read(ref _lastRetrieveLatencyMs);

        public async Task<string?> GetAsync(string key)
        {
            RedisValue value = await _db.StringGetAsync(key);
            return value.IsNull ? null : value.ToString();
        }

        public Task SetAsync(string key, string value, TimeSpan expiry)
        {
            return _db.StringSetAsync(key, value, expiry);
        }

        public async Task<double> ProbeLatencyMsAsync(string probeId)
        {
            string cacheKey = $"context:probe:{probeId}";
            var sw = Stopwatch.StartNew();

            string? context = await GetAsync(cacheKey);
            context ??= $"HUR OMEGA Probe Kontext: '{probeId}'";
            await SetAsync(cacheKey, context, TimeSpan.FromMinutes(5));

            sw.Stop();
            Volatile.Write(ref _lastRetrieveLatencyMs, sw.Elapsed.TotalMilliseconds);
            return sw.Elapsed.TotalMilliseconds;
        }

        public async Task<string> RetrieveHyperCognitiveContext(string query)
        {
            var sw = Stopwatch.StartNew();
            string cacheKey = $"context:{query}";
            string? context = await GetAsync(cacheKey);
            if (context == null)
            {
                System.Threading.Interlocked.Increment(ref _cacheMisses);
                context = $"HUR OMEGA Kontext: Praediktion zu '{query}' (DB-Fallback)";
                await SetAsync(cacheKey, context, TimeSpan.FromMinutes(5));
            }
            else
            {
                System.Threading.Interlocked.Increment(ref _cacheHits);
                await SetAsync(cacheKey, context, TimeSpan.FromMinutes(5));
            }

            sw.Stop();
            Volatile.Write(ref _lastRetrieveLatencyMs, sw.Elapsed.TotalMilliseconds);

            return context;
        }
    }

    public class ContextualMemoryHandler
    {
        private readonly HoloKognitivesRepository _repository;

        public ContextualMemoryHandler(HoloKognitivesRepository repository)
        {
            _repository = repository;
        }

        public async Task DeliverPreventiveContext(string agentId)
        {
            string context = await _repository.RetrieveHyperCognitiveContext($"Praevention {agentId}");
            Console.WriteLine($"[CHM OMEGA] {agentId} erhaelt praeventiven Kontext: {context}");
        }

        public (long Hits, long Misses) GetCacheStats() => _repository.GetCacheStats();

        public double GetLastCacheLatencyMs() => _repository.GetLastRetrieveLatencyMs();

        public Task<double> ProbeCacheLatencyMsAsync(string probeId) => _repository.ProbeLatencyMsAsync(probeId);
    }
}
