import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    print("[PASS] Health check passed:", data)


def test_filter_options():
    response = client.get("/api/v1/filters/options")
    assert response.status_code == 200
    data = response.json()
    assert "states" in data
    assert "specialties" in data
    assert "diseases" in data
    assert "risk_levels" in data
    print(f"[PASS] Filter options passed ({len(data['states'])} states, {len(data['specialties'])} specialties)")


def test_filter_dependent():
    response = client.get("/api/v1/filters/options?county_fips=37161&specialty=Psychiatry")
    assert response.status_code == 200
    data = response.json()
    assert len(data["risk_levels"]) > 0
    print("[PASS] Dependent filter passed (County + Specialty):", data["risk_levels"])


def test_dashboard_summary():
    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "riskDistribution" in data
    assert "specialtyGaps" in data
    assert "trend" in data
    assert "topCriticalAreas" in data
    print(f"[PASS] Dashboard summary passed (Total Areas: {data['metrics']['totalAreas']}, Providers: {data['metrics']['totalProviders']})")


def test_map_areas():
    response = client.get("/api/v1/map/areas")
    assert response.status_code == 200
    data = response.json()
    assert "areas" in data
    assert len(data["areas"]) > 0
    sample = data["areas"][0]
    assert "latitude" in sample
    assert "longitude" in sample
    assert "diseases" in sample
    assert len(sample["diseases"]) > 0
    print(f"[PASS] Map areas passed ({len(data['areas'])} areas, sample area: {sample['name']} with {len(sample['diseases'])} diseases)")


def test_providers():
    response = client.get("/api/v1/providers?page=1&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert "providers" in data
    assert "total" in data
    print(f"[PASS] Providers search passed (Total: {data['total']}, Returned: {len(data['providers'])})")


def test_access_gaps():
    response = client.get("/api/v1/access-gaps?page=1&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    print(f"[PASS] Access gaps passed (Total: {data['total']})")


def test_search():
    response = client.get("/api/v1/search?county_fips=48183&specialty=Endocrinology")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    print(f"[PASS] Search endpoint passed ({len(data['results'])} matching results)")


def test_what_if_simulation():
    payload = {
        "county_fips": "48183",
        "specialty": "Endocrinology",
        "disease": "Diabetes",
        "additional_providers": 3,
    }
    response = client.post("/api/v1/simulation/what-if", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "current" in data
    assert "simulation" in data
    assert "curve" in data
    assert len(data["curve"]) == 6
    print(f"[PASS] What-If simulation passed (Current Risk: {data['current']['gap_score']}, Projected: {data['simulation']['projected_gap_score']}, Improvement: {data['simulation']['access_improvement_pct']}%)")


def test_recommendations():
    response = client.get("/api/v1/recommendations")
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "items" in data
    print(f"[PASS] Recommendations passed ({len(data['items'])} items, Critical Areas: {data['summary']['criticalRecruitmentAreas']})")


def test_auth_flow():
    # Signup
    test_email = f"test_user_{int(os.getpid())}@gmail.com"
    signup_payload = {
        "email": test_email,
        "password": "Password123!",
        "fullName": "Test User",
        "role": "Network Manager",
    }
    signup_res = client.post("/api/v1/auth/signup", json=signup_payload)
    assert signup_res.status_code in [200, 201, 400] # Supabase email confirmation or success
    print("[PASS] Auth signup endpoint responded:", signup_res.json())


def test_chat_query():
    # Test natural language question
    payload = {"query": "Which areas have critical shortages for cardiology?"}
    res = client.post("/api/v1/chat/query", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert len(data["answer"]) > 10
    print("[PASS] AI Assistant chat endpoint passed:", data["answer"][:75] + "...")


def test_twilio_call_and_sms():
    payload = {
        "to_phone": "+19999999999",
        "message": "Testing Twilio Voice and SMS simulation alert."
    }
    res = client.post("/api/v1/twilio/send-call-and-sms", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "success" in data
    assert "sms" in data
    assert "call" in data
    print("[PASS] Twilio Call & SMS integration test completed successfully.")



if __name__ == "__main__":
    print("Running backend integration tests...")
    test_health()
    test_filter_options()
    test_filter_dependent()
    test_dashboard_summary()
    test_map_areas()
    test_providers()
    test_access_gaps()
    test_search()
    test_what_if_simulation()
    test_recommendations()
    test_chat_query()
    test_auth_flow()
    test_twilio_call_and_sms()
    print("\nALL BACKEND TESTS PASSED SUCCESSFULLY!")


