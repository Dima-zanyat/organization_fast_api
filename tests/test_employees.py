"""Test cases for employees API."""

import pytest
from tests.conftest import client


class TestEmployeeCreation:
    """Test employee creation endpoint."""

    def test_create_employee_success(self):
        """Test successful employee creation."""
        dept = client.post("/departments/", json={"name": "Backend"}).json()
        response = client.post(
            f"/departments/{dept['id']}/employees/",
            json={"full_name": "John Doe", "position": "Senior Developer"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["full_name"] == "John Doe"
        assert data["position"] == "Senior Developer"

    def test_create_employee_with_hire_date(self):
        """Test creating employee with hire date."""
        dept = client.post("/departments/", json={"name": "Backend"}).json()
        response = client.post(
            f"/departments/{dept['id']}/employees/",
            json={
                "full_name": "John Doe",
                "position": "Developer",
                "hired_at": "2023-01-15",
            },
        )
        assert response.status_code == 201

    def test_create_employee_empty_name(self):
        """Test creating employee with empty name."""
        dept = client.post("/departments/", json={"name": "Backend"}).json()
        response = client.post(
            f"/departments/{dept['id']}/employees/",
            json={"full_name": "   ", "position": "Developer"},
        )
        assert response.status_code == 400

    def test_create_employee_empty_position(self):
        """Test creating employee with empty position."""
        dept = client.post("/departments/", json={"name": "Backend"}).json()
        response = client.post(
            f"/departments/{dept['id']}/employees/",
            json={"full_name": "John", "position": ""},
        )
        assert response.status_code == 400

    def test_create_employee_nonexistent_department(self):
        """Test creating employee in nonexistent department."""
        response = client.post(
            "/departments/999/employees/",
            json={"full_name": "John", "position": "Developer"},
        )
        assert response.status_code == 404
