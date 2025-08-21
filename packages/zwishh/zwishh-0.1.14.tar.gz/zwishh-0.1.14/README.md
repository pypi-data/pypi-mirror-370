# 🧰 zwishh – Internal SDK and Utilities

This package provides shared utilities and client SDKs for Zwishh's internal microservices.

It is intended for **internal use only** and should be used by trusted services inside the Zwishh platform infrastructure.

---

## 📦 What's Included

### 🔑 Authentication & Security
- `verify_service_api_key_dep`: FastAPI dependency for verifying internal service API keys
- `get_current_user_id_dep`: Extracts and validates the current authenticated user from headers

### 🧬 SDK Clients
Clients for accessing core Zwishh services:

- `OrdersClient` – create & fetch orders
- `CartClient` – manage cart state
- `DeliveryClient` – manage delivery state
- `CouponClient` – manage coupon state
- `InteractionClient` – manage interaction state
- `UserServiceClient` – manage user state
- `SellerServiceClient` – manage seller state


Each client:
- Uses async `httpx`
- Injects service-to-service API key headers
- Handles standard error responses
- Retries the request with exponential backoff

---

## 🛠 Installation

You can install it directly from PyPI:

```bash
pip install zwishh
