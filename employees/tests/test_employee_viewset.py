
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User, Group
from rest_framework.authtoken.models import Token
from employees.models import Employee, Department


class EmployeeViewSetPermissionTests(APITestCase):
    def setUp(self):
        # Create Departments
        self.dept_eng = Department.objects.create(name="EngDept")
        self.dept_hr = Department.objects.create(name="AB")

        # Create groups
        self.admin_group = Group.objects.create(name="Admin")
        self.hr_group = Group.objects.create(name="HR")
        self.emp_group = Group.objects.create(name="Employee")

        # Create an Admin user
        self.admin_user = User.objects.create_user(username="admin", password="pass123")
        self.admin_user.is_staff = True
        self.admin_user.is_superuser = True
        self.admin_user.save()
        self.admin_group.user_set.add(self.admin_user)
        self.admin_token = Token.objects.create(user=self.admin_user)

        # Create an HR user
        self.hr_user = User.objects.create_user(username="hr", password="pass123")
        self.hr_user.is_staff = True
        self.hr_user.save()
        self.hr_group.user_set.add(self.hr_user)
        self.hr_token = Token.objects.create(user=self.hr_user)

        # Create two Employee users
        self.emp_user1 = User.objects.create_user(username="alice", password="pass123")
        self.emp_user1.save()
        self.emp_group.user_set.add(self.emp_user1)
        self.emp_token1 = Token.objects.create(user=self.emp_user1)

        self.emp_user2 = User.objects.create_user(username="bob", password="pass123")
        self.emp_user2.save()
        self.emp_group.user_set.add(self.emp_user2)
        self.emp_token2 = Token.objects.create(user=self.emp_user2)

        # Create Employee records linked to those users
        self.emp_record1 = Employee.objects.create(
            name="Alice",
            email="alice@example.com",
            phone_number="1112223333",
            address="123 St",
            date_of_joining="2024-01-01",
            department=self.dept_eng,
            user=self.emp_user1
        )
        self.emp_record2 = Employee.objects.create(
            name="Bob",
            email="bob@example.com",
            phone_number="4445556666",
            address="456 Ave",
            date_of_joining="2024-02-01",
            department=self.dept_hr,
            user=self.emp_user2
        )

    def test_employee_list_allowed_for_all(self):
        """
        All roles (Employee, HR, Admin) may GET the list of employees (200 OK).
        """
        url = reverse('employee-list')  # e.g. /api/employees/employees/

        # As an Employee
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.emp_token1.key}")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 2)

        # As HR
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.hr_token.key}")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 2)

        # As Admin
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 2)

    def test_employee_retrieve_allowed_for_all(self):
        """
        All roles may GET (retrieve) any single employee by ID (200 OK).
        """
        url1 = reverse('employee-detail', kwargs={'pk': self.emp_record1.pk})
        url2 = reverse('employee-detail', kwargs={'pk': self.emp_record2.pk})

        # Employee1 retrieving Employee2’s record
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.emp_token1.key}")
        response = self.client.get(url2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Bob")

        # HR retrieving Employee1’s record
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.hr_token.key}")
        response = self.client.get(url1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Alice")

        # Admin retrieving Employee2’s record
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        response = self.client.get(url2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Bob")

    def test_employee_create(self):
        """
        Only Admin may POST a new Employee record (201 Created).
        HR and Employee should get 403 FORBIDDEN.
        """
        url = reverse('employee-list')
        payload = {
            "name": "Charlie",
            "email": "charlie@example.com",
            "phone_number": "7778889999",
            "address": "789 Blvd",
            "date_of_joining": "2024-03-01",
            "department_id": self.dept_eng.id,
            "user": self.emp_user1.id

        }

        # As Employee → should be forbidden
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.emp_token1.key}")
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Employee.objects.filter(name="Charlie").exists())

        # As HR → should be forbidden
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.hr_token.key}")
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Employee.objects.filter(name="Charlie").exists())

        # As Admin → should succeed
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Employee.objects.filter(name="Charlie").exists())

    def test_employee_update(self):
        """
        HR and Admin may PUT/PATCH to update any Employee.
        Employee (non‐HR) may not update any (403).
        """
        url1 = reverse('employee-detail', kwargs={'pk': self.emp_record1.pk})
        update_payload = {
            "name": "Alice Updated",
            "email": "alice_new@example.com",
            "phone_number": "9998887777",
            "address": "321 New St",
            "date_of_joining": "2024-01-01",
            "department_id": self.dept_hr.id,
            "user": self.emp_user1.id
        }

        # As Employee1 updating self or others → forbidden
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.emp_token1.key}")
        response = self.client.put(url1, update_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Ensure name did not change
        self.emp_record1.refresh_from_db()
        self.assertEqual(self.emp_record1.name, "Alice")

        # As HR updating Employee1 → allowed
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.hr_token.key}")
        response = self.client.put(url1, update_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.emp_record1.refresh_from_db()
        self.assertEqual(self.emp_record1.name, "Alice Updated")
        self.assertEqual(self.emp_record1.email, "alice_new@example.com")

        # Reset name for next test
        self.emp_record1.name = "Alice"
        self.emp_record1.email = "alice@example.com"
        self.emp_record1.department = self.dept_eng
        self.emp_record1.save()

        # As Admin updating Employee2 → allowed
        url2 = reverse('employee-detail', kwargs={'pk': self.emp_record2.pk})
        update_payload2 = {
            "name": "Bob Updated",
            "email": "bob_new@example.com",
            "phone_number": "4445556666",
            "address": "456 Ave",
            "date_of_joining": "2024-02-01",
            "department": self.dept_hr.id,
            "user": self.emp_user2.id
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        response = self.client.patch(url2, {"name": "Bob Updated"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.emp_record2.refresh_from_db()
        self.assertEqual(self.emp_record2.name, "Bob Updated")

    def test_employee_delete(self):
        """
        Only Admin may DELETE an Employee record (204 No Content).
        HR and Employee should get 403 FORBIDDEN.
        """
        url = reverse('employee-detail', kwargs={'pk': self.emp_record1.pk})

        # As Employee → forbidden
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.emp_token1.key}")
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Employee.objects.filter(pk=self.emp_record1.pk).exists())

        # As HR → forbidden (HR may modify but not delete)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.hr_token.key}")
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Employee.objects.filter(pk=self.emp_record1.pk).exists())

        # As Admin → allowed
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Employee.objects.filter(pk=self.emp_record1.pk).exists())
