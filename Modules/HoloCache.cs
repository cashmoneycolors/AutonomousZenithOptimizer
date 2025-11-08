using System;
using System.Collections.Generic;
using System.Threading.Tasks;
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

    public class HoloKognitivesRepository : IHyperCache
    {
        private readonly IDatabase _db;

        public HoloKognitivesRepository(IConnectionMultiplexer redis)
        {
            _db = redis.GetDatabase(0);
        }

        public async Task<string?> GetAsync(string key)
        {
            RedisValue value = await _db.StringGetAsync(key);
            return value.IsNull ? null : value.ToString();
        }

        public Task SetAsync(string key, string value, TimeSpan expiry)
        {
            return _db.StringSetAsync(key, value, expiry);
        }

        public async Task<string> RetrieveHyperCognitiveContext(string query)
        {
            string cacheKey = $"context:{query}";
            string? context = await GetAsync(cacheKey);
            if (context == null)
            {
                context = $"HUR OMEGA Kontext: Praediktion zu '{query}' (DB-Fallback)";
                await SetAsync(cacheKey, context, TimeSpan.FromMinutes(5));
            }
            else
            {
                await SetAsync(cacheKey, context, TimeSpan.FromMinutes(5));
            }

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
    }
}
