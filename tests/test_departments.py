"""Test cases for departments API."""

import pytest
from tests.conftest import client


class TestDepartmentCreation:
    """Test department creation endpoint."""

    def test_create_department_success(self):
        """Test successful department creation."""
        response = client.post(
            "/departments/", json={"name": "Backend", "parent_id": None}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Backend"
        assert data["parent_id"] is None
        assert "id" in data

    def test_create_department_with_parent(self):
        """Test creating department with parent."""
        # Create parent first
        parent_response = client.post("/departments/", json={"name": "Engineering"})
        parent_id = parent_response.json()["id"]

        # Create child
        response = client.post(
            "/departments/", json={"name": "Backend", "parent_id": parent_id}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["parent_id"] == parent_id

    def test_create_department_empty_name(self):
        """Test creating department with empty name."""
        response = client.post("/departments/", json={"name": "   "})
        assert response.status_code == 400

    def test_create_department_duplicate_name_in_parent(self):
        """Test creating duplicate department name in same parent."""
        client.post("/departments/", json={"name": "Backend"})
        response = client.post("/departments/", json={"name": "Backend"})
        assert response.status_code == 400

    def test_create_department_nonexistent_parent(self):
        """Test creating department with nonexistent parent."""
        response = client.post(
            "/departments/", json={"name": "Backend", "parent_id": 999}
        )
        assert response.status_code == 400


class TestDepartmentRetrieval:
    """Test department retrieval endpoint."""

    def test_get_department_success(self):
        """Test successful department retrieval."""
        created = client.post("/departments/", json={"name": "Backend"})
        dept_id = created.json()["id"]

        response = client.get(f"/departments/{dept_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == dept_id
        assert data["name"] == "Backend"

    def test_get_department_with_employees(self):
        """Test getting department with employees."""
        dept = client.post("/departments/", json={"name": "Backend"}).json()
        dept_id = dept["id"]

        # Add employee
        client.post(
            f"/departments/{dept_id}/employees/",
            json={"full_name": "John Doe", "position": "Developer"},
        )

        response = client.get(f"/departments/{dept_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["employees"]) == 1
        assert data["employees"][0]["full_name"] == "John Doe"

    def test_get_department_not_found(self):
        """Test getting nonexistent department."""
        response = client.get("/departments/999")
        assert response.status_code == 404

    def test_get_department_with_tree(self):
        """Test getting department with children tree."""
        # Create parent
        parent = client.post("/departments/", json={"name": "Engineering"}).json()
        parent_id = parent["id"]

        # Create children
        child1 = client.post(
            "/departments/", json={"name": "Backend", "parent_id": parent_id}
        ).json()
        child2 = client.post(
            "/departments/", json={"name": "Frontend", "parent_id": parent_id}
        ).json()

        # Get parent with tree
        response = client.get(f"/departments/{parent_id}?depth=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["children"]) == 2
        assert data["children"][0]["name"] in ["Backend", "Frontend"]


class TestDepartmentUpdate:
    """Test department update endpoint."""

    def test_update_department_name(self):
        """Test updating department name."""
        dept = client.post("/departments/", json={"name": "Backend"}).json()
        dept_id = dept["id"]

        response = client.patch(
            f"/departments/{dept_id}", json={"name": "Backend Services"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Backend Services"

    def test_update_department_parent(self):
        """Test updating department parent."""
        parent1 = client.post("/departments/", json={"name": "Parent1"}).json()
        parent2 = client.post("/departments/", json={"name": "Parent2"}).json()
        child = client.post(
            "/departments/", json={"name": "Child", "parent_id": parent1["id"]}
        ).json()

        response = client.patch(
            f"/departments/{child['id']}", json={"parent_id": parent2["id"]}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["parent_id"] == parent2["id"]

    def test_update_department_cannot_be_own_parent(self):
        """Test that department cannot be its own parent."""
        dept = client.post("/departments/", json={"name": "Backend"}).json()
        response = client.patch(
            f"/departments/{dept['id']}", json={"parent_id": dept["id"]}
        )
        assert response.status_code == 400

    def test_update_department_cycle_detection(self):
        """Test cycle detection in tree."""
        parent = client.post("/departments/", json={"name": "Parent"}).json()
        child = client.post(
            "/departments/", json={"name": "Child", "parent_id": parent["id"]}
        ).json()

        # Try to make parent a child of child (creates cycle)
        response = client.patch(
            f"/departments/{parent['id']}", json={"parent_id": child["id"]}
        )
        assert response.status_code == 409


class TestDepartmentDelete:
    """Test department deletion endpoint."""

    def test_delete_department_cascade(self):
        """Test cascade delete."""
        dept = client.post("/departments/", json={"name": "Backend"}).json()
        dept_id = dept["id"]

        # Add employee
        client.post(
            f"/departments/{dept_id}/employees/",
            json={"full_name": "John", "position": "Dev"},
        )

        response = client.delete(f"/departments/{dept_id}?mode=cascade")
        assert response.status_code == 204

        # Verify deleted
        get_response = client.get(f"/departments/{dept_id}")
        assert get_response.status_code == 404

    def test_delete_department_reassign(self):
        """Test reassign delete."""
        dept1 = client.post("/departments/", json={"name": "Dept1"}).json()
        dept2 = client.post("/departments/", json={"name": "Dept2"}).json()

        # Add employee to dept1
        emp = client.post(
            f"/departments/{dept1['id']}/employees/",
            json={"full_name": "John", "position": "Dev"},
        ).json()

        # Reassign delete
        response = client.delete(
            f"/departments/{dept1['id']}?mode=reassign&reassign_to_department_id={dept2['id']}"
        )
        assert response.status_code == 204

        # Verify employee moved
        emp_response = client.get(f"/departments/{dept2['id']}")
        assert len(emp_response.json()["employees"]) == 1
