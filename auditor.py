#!/usr/bin/env python3
import hashlib
import argparse
import time
import json
from multiprocessing import Pool, cpu_count

def hash_text(text, algo):
    if algo == "md5":
        return hashlib.md5(text.encode()).hexdigest()
    elif algo == "sha256":
        return hashlib.sha256(text.encode()).hexdigest()

def mutate(word):
    mutations = set()
    mutations.add(word)
    mutations.add(word.lower())
    mutations.add(word.upper())
    mutations.add(word.capitalize())

    for i in range(0, 100):
        mutations.add(f"{word}{i}")

    symbols = ["!", "@", "#"]
    for s in symbols:
        mutations.add(word + s)

    return mutations

def worker(args):
    chunk, target_hash, algo = args
    for word in chunk:
        if hash_text(word, algo) == target_hash:
            return word
    return None

def chunkify(lst, n):
    k = max(1, len(lst) // n)
    for i in range(0, len(lst), k):
        yield lst[i:i + k]

def load_wordlist(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return [line.strip() for line in f if line.strip()]

def run_attack(target_hash, wordlist, algo, use_mutation):
    if use_mutation:
        mutated = set()
        for w in wordlist:
            mutated.update(mutate(w))
        wordlist = list(mutated)

    chunks = list(chunkify(wordlist, cpu_count()))
    args = [(chunk, target_hash, algo) for chunk in chunks]

    with Pool(cpu_count()) as pool:
        results = pool.map(worker, args)

    for r in results:
        if r:
            return r
    return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hash", required=True)
    parser.add_argument("--algo", default="md5")
    parser.add_argument("--wordlist", required=True)
    parser.add_argument("--mutate", action="store_true")

    args = parser.parse_args()

    wordlist = load_wordlist(args.wordlist)
    result = run_attack(args.hash, wordlist, args.algo, args.mutate)

    if result:
        print(f"[FOUND] {result}")
    else:
        print("Not found")

if __name__ == "__main__":
    main()