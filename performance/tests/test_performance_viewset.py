# performance/tests/test_performance_viewset.py

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User, Group
from rest_framework.authtoken.models import Token
from employees.models import Employee, Department
from performance.models import Performance


class PerformanceViewSetPermissionTests(APITestCase):
    def setUp(self):
        # Create Departments (names ≤10 chars)
        self.dept_eng = Department.objects.create(name="EngDept")
        self.dept_hr = Department.objects.create(name="AB")

        # Create Groups
        self.admin_group = Group.objects.create(name="Admin")
        self.hr_group = Group.objects.create(name="HR")
        self.emp_group = Group.objects.create(name="Employee")

        # Create Admin user
        self.admin_user = User.objects.create_user(username="admin", password="password")
        self.admin_user.is_staff = True
        self.admin_user.is_superuser = True
        self.admin_user.save()
        self.admin_group.user_set.add(self.admin_user)
        self.admin_token = Token.objects.create(user=self.admin_user)

        # Create HR user
        self.hr_user = User.objects.create_user(username="hr", password="password")
        self.hr_user.is_staff = True
        self.hr_user.save()
        self.hr_group.user_set.add(self.hr_user)
        self.hr_token = Token.objects.create(user=self.hr_user)

        # Create Employee users & records (phone_number ≤10 chars)
        self.emp_user1 = User.objects.create_user(username="alice", password="password")
        self.emp_user1.save()
        self.emp_group.user_set.add(self.emp_user1)
        self.emp_token1 = Token.objects.create(user=self.emp_user1)

        self.emp_record1 = Employee.objects.create(
            name="Alice",
            email="alice@example.com",
            phone_number="1234567890",  # Exactly 10 chars
            address="123 Elm St",
            date_of_joining="2024-01-01",
            department=self.dept_eng,
            user=self.emp_user1
        )

        self.emp_user2 = User.objects.create_user(username="bob", password="password")
        self.emp_user2.save()
        self.emp_group.user_set.add(self.emp_user2)
        self.emp_token2 = Token.objects.create(user=self.emp_user2)

        self.emp_record2 = Employee.objects.create(
            name="Bob",
            email="bob@example.com",
            phone_number="0987654321",  # Exactly 10 chars
            address="456 Oak Ave",
            date_of_joining="2024-02-01",
            department=self.dept_hr,
            user=self.emp_user2
        )

        # Create sample Performance entries
        self.perf1 = Performance.objects.create(
            employee=self.emp_record1,
            date="2025-05-15",
            score=85
        )
        self.perf2 = Performance.objects.create(
            employee=self.emp_record2,
            date="2025-05-20",
            score=92
        )

    def test_performance_list_allowed_for_all(self):
        """
        All roles (Employee, HR, Admin) should GET the list of performance records (200 OK).
        """
        url = reverse('performance-list')

        # As Employee1
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

    def test_performance_retrieve_allowed_for_all(self):
        """
        All roles (Employee, HR, Admin) should GET (retrieve) any single performance record by ID.
        """
        url1 = reverse('performance-detail', kwargs={'pk': self.perf1.pk})
        url2 = reverse('performance-detail', kwargs={'pk': self.perf2.pk})

        # Employee1 retrieving perf2
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.emp_token1.key}")
        response = self.client.get(url2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['score'], 92)

        # HR retrieving perf1
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.hr_token.key}")
        response = self.client.get(url1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['score'], 85)

        # Admin retrieving perf2
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        response = self.client.get(url2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['score'], 92)

    def test_performance_create(self):
        """
        Only Admin may POST a new Performance record. HR and Employee should get 403.
        """
        url = reverse('performance-list')
        payload = {
            "employee": self.emp_record1.id,
            "date": "2025-06-01",
            "score": 78
        }

        # As Employee → forbidden
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.emp_token1.key}")
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Performance.objects.filter(date="2025-06-01", score=78).exists())

        # As HR → forbidden
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.hr_token.key}")
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Performance.objects.filter(date="2025-06-01", score=78).exists())

        # As Admin → allowed
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Performance.objects.filter(date="2025-06-01", score=78).exists())

    def test_performance_update(self):
        """
        HR and Admin may PUT/PATCH to update any Performance. Employee may not update (403).
        """
        url = reverse('performance-detail', kwargs={'pk': self.perf1.pk})
        update_payload = {"score": 88}

        # As Employee → forbidden
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.emp_token1.key}")
        response = self.client.patch(url, update_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.perf1.refresh_from_db()
        self.assertEqual(self.perf1.score, 85)

        # As HR → allowed
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.hr_token.key}")
        response = self.client.patch(url, update_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.perf1.refresh_from_db()
        self.assertEqual(self.perf1.score, 88)

        # Reset score
        self.perf1.score = 85
        self.perf1.save()

        # As Admin → allowed
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        response = self.client.patch(url, update_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.perf1.refresh_from_db()
        self.assertEqual(self.perf1.score, 88)

    def test_performance_delete(self):
        """
        Only Admin may DELETE a Performance record. HR and Employee should get 403.
        """
        url = reverse('performance-detail', kwargs={'pk': self.perf2.pk})

        # As Employee → forbidden
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.emp_token2.key}")
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Performance.objects.filter(pk=self.perf2.pk).exists())

        # As HR → forbidden
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.hr_token.key}")
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Performance.objects.filter(pk=self.perf2.pk).exists())

        # As Admin → allowed
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Performance.objects.filter(pk=self.perf2.pk).exists())
