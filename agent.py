import os
import json
import time
import hashlib
import threading
from typing import Dict, Any, List, Literal, Annotated, TypedDict
import numpy as np
from collections import deque
import random
import requests
from torch.distributions import Categorical, Normal
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

# Try imports with fallbacks
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ModuleNotFoundError:
    OPENAI_AVAILABLE = False
    class MockOpenAI:
        class chat:
            class completions:
                def create(self, **kwargs):
                    return type('obj', (object,), {
                        'choices': [type('obj', (object,), {
                            'message': type('obj', (object,), {'content': 'Mock response'})
                        })]
                    })()

try:
    import gymnasium as gym
    GYM_AVAILABLE = True
except ModuleNotFoundError:
    GYM_AVAILABLE = False
    print("Gymnasium not found – Using Mock. Install with: pip install gymnasium")

try:
    from pydantic import BaseModel, ValidationError
    PYDANTIC_AVAILABLE = True
except ModuleNotFoundError:
    PYDANTIC_AVAILABLE = False
    class BaseModel: pass
    ValidationError = ValueError

# Load environment variables from .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Environment Vars
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
XAI_API_KEY = os.getenv('XAI_API_KEY')
BLACKBOX_API_KEY = os.getenv('BLACKBOX_API_KEY')

# Persistent Cache & State
CACHE_FILE = 'agent_cache.json'
STATE_FILE = 'agent_state.json'
cache = {}
current_state: Dict = {}

def load_cache():
    global cache
    try:
        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)
    except FileNotFoundError:
        cache = {}

def save_cache():
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=4)

def load_state():
    global current_state
    try:
        with open(STATE_FILE, 'r') as f:
            current_state = json.load(f)
    except FileNotFoundError:
        current_state = {"messages": [], "next_step": "start", "token_budget": 10000, "latency_log": []}

def save_state():
    with open(STATE_FILE, 'w') as f:
        json.dump(current_state, f, indent=4)

load_cache()
load_state()

# State Schema
class AgentState(TypedDict):
    messages: Annotated[List[Dict[str, str]], "Chat history"]
    next_step: Literal["start", "plan", "execute", "reflect", "retry", "finish"]
    token_budget: int
    latency_log: List[float]

class StructuredOutput(BaseModel):
    action: str
    content: str
    confidence: float

# RL Components
class ReplayBuffer:
    def __init__(self, capacity):
        self.buffer = deque(maxlen=capacity)

    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size):
        batch = random.sample(self.buffer, batch_size)
        state, action, reward, next_state, done = map(np.stack, zip(*batch))
        return state, action, reward, next_state, done

    def __len__(self):
        return len(self.buffer)

# PPO Discrete GAE (Fixed non-inplace Relu)
class PPOActorCritic(nn.Module):
    def __init__(self, state_dim=4, action_dim=2):
        super().__init__()
        self.fc1 = nn.Linear(state_dim, 64)
        self.fc2 = nn.Linear(64, 64)
        self.actor = nn.Linear(64, action_dim)
        self.critic = nn.Linear(64, 1)
    
    def forward(self, state):
        x = F.relu(self.fc1(state), inplace=False)  # Explicit non-inplace
        x = F.relu(self.fc2(x), inplace=False)
        logits = self.actor(x)
        policy = F.softmax(logits, dim=-1)
        value = self.critic(x)
        return policy, value

def compute_gae(rewards, values, next_value, dones, gamma=0.99, lam=0.95):
    advantages = []
    gae = 0
    for step in reversed(range(len(rewards))):
        if step == len(rewards) - 1:
            next_non_terminal = 1.0 - dones[step]
            next_val = next_value
        else:
            next_non_terminal = 1.0 - dones[step]
            next_val = values[step + 1]
        delta = rewards[step] + gamma * next_val * next_non_terminal - values[step]
        gae = delta + gamma * lam * next_non_terminal * gae
        advantages.insert(0, gae)
    return advantages

if __name__ == "__main__":
    print("Agent initialized successfully")
