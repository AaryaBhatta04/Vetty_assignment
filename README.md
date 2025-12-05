# CoinGecko Flask API

This project is my attempt at implementing a small Flask API wrapper around the CoinGecko public API with JWT authentication and simple pagination.

## Features

* Login endpoint returning JWT tokens
* Protected API routes using `Bearer <token>`
* Fetch list of coins and categories
* Filter coins by `ids` or category
* Prices returned in **INR** and **CAD**
* Minimal in‑memory pagination

## Setup

Install requirements:

```bash
pip install Flask requests PyJWT
```

Run the server:

```bash
python app.py
```

The app runs on: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

## Authentication

`POST /auth/login`

```json
{ "username": "Aaryaman Bhattacharya", "password": "Aaryaman@04" }
```

Returns a JWT token to use in all subsequent requests:

```
Authorization: Bearer <token>
```

## Endpoints

### 1. `GET /api/coins`

Returns the CoinGecko coin list with simple pagination.
Query parameters:

* `page_num` (default 1)
* `per_page` (default 10)

### 2. `GET /api/categories`

Returns the list of categories, also paginated.

### 3. `GET /api/coins/filter`

Filters coins based on:

* `ids` — comma‑separated
* `category` — comma‑separated

The API fetches data in both INR and CAD and merges them into a single list.
Supports the same pagination parameters.

## Pagination

Each list endpoint returns:

```json
{
  "page_num": 1,
  "per_page": 10,
  "total_items": ...,   
  "total_pages": ...,   
  "items": [ ... ]
}
```

## Notes (Contest Constraints)

* Users are hard‑coded (no database)
* Error handling is minimal but functional
* No caching due to time limitation

## Summary

This project demonstrates:

* Basic Flask API design
* JWT‑protected endpoints
* External API integration (CoinGecko)
* Simple pagination & merging across currencies