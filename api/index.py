{
  "functions": {
    "index.py": {
      "runtime": "now-python@3.9"
    }
  },
  "routes": [
    {
      "src": "/(.*)",
      "dest": "index.py"
    }
  ]
}
