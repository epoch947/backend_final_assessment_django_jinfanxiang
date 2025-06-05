
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User, Group
from rest_framework.authtoken.models import Token
from employees.models import Employee, Department
from attendance.models import Attendance


class AttendanceViewSetPermissionTests(APITestCase):
    def setUp(self):
        # Use names ≤ 10 chars to avoid DataError
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

        # Create two Employee users and corresponding Employee records
        self.emp_user1 = User.objects.create_user(username="alice", password="pass123")
        self.emp_user1.save()
        self.emp_group.user_set.add(self.emp_user1)
        self.emp_token1 = Token.objects.create(user=self.emp_user1)
        self.emp_record1 = Employee.objects.create(
            name="Alice",
            email="alice@example.com",
            phone_number="1112223333",
            address="123 St",
            date_of_joining="2024-01-01",
            department=self.dept_eng,
            user=self.emp_user1
        )

        self.emp_user2 = User.objects.create_user(username="bob", password="pass123")
        self.emp_user2.save()
        self.emp_group.user_set.add(self.emp_user2)
        self.emp_token2 = Token.objects.create(user=self.emp_user2)
        self.emp_record2 = Employee.objects.create(
            name="Bob",
            email="bob@example.com",
            phone_number="4445556666",
            address="456 Ave",
            date_of_joining="2024-02-01",
            department=self.dept_hr,
            user=self.emp_user2
        )

        # Create two Attendance records
        self.att1 = Attendance.objects.create(
            employee=self.emp_record1,
            date="2025-06-01",
            status="present"
        )
        self.att2 = Attendance.objects.create(
            employee=self.emp_record2,
            date="2025-06-02",
            status="absent"
        )

    def test_attendance_list_allowed_for_all(self):
        """
        All roles (Employee, HR, Admin) may GET the list of attendance records (200 OK).
        """
        url = reverse('attendance-list')

        # As Employee
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

    def test_attendance_retrieve_allowed_for_all(self):
        """
        All roles may GET (retrieve) any single attendance record by ID (200 OK).
        """
        url1 = reverse('attendance-detail', kwargs={'pk': self.att1.pk})
        url2 = reverse('attendance-detail', kwargs={'pk': self.att2.pk})

        # Employee retrieving someone else's attendance
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.emp_token1.key}")
        response = self.client.get(url2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "absent")

        # HR retrieving attendance
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.hr_token.key}")
        response = self.client.get(url1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "present")

        # Admin retrieving attendance
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        response = self.client.get(url2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "absent")

    def test_attendance_create(self):
        """
        Only Admin may POST a new Attendance record.
        HR and Employee should get 403 FORBIDDEN.
        """
        url = reverse('attendance-list')
        payload = {
            "employee": self.emp_record1.id,
            "date": "2025-06-10",
            "status": "present"
        }

        # As Employee → forbidden
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.emp_token1.key}")
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Attendance.objects.filter(date="2025-06-10").exists())

        # As HR → forbidden
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.hr_token.key}")
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Attendance.objects.filter(date="2025-06-10").exists())

        # As Admin → allowed
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Attendance.objects.filter(date="2025-06-10").exists())

    def test_attendance_update(self):
        """
        HR and Admin may PUT/PATCH to update any Attendance.
        Employee may not update any (403).
        """
        url = reverse('attendance-detail', kwargs={'pk': self.att1.pk})
        update_payload = {"status": "absent"}

        # As Employee → forbidden
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.emp_token1.key}")
        response = self.client.patch(url, update_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.att1.refresh_from_db()
        self.assertEqual(self.att1.status, "present")

        # As HR → allowed
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.hr_token.key}")
        response = self.client.patch(url, update_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.att1.refresh_from_db()
        self.assertEqual(self.att1.status, "absent")

        # Reset status
        self.att1.status = "present"
        self.att1.save()

        # As Admin → allowed
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        response = self.client.patch(url, update_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.att1.refresh_from_db()
        self.assertEqual(self.att1.status, "absent")

    def test_attendance_delete(self):
        """
        Only Admin may DELETE an Attendance record.
        HR and Employee should get 403 FORBIDDEN.
        """
        url = reverse('attendance-detail', kwargs={'pk': self.att2.pk})

        # As Employee → forbidden
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.emp_token2.key}")
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Attendance.objects.filter(pk=self.att2.pk).exists())

        # As HR → forbidden
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.hr_token.key}")
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Attendance.objects.filter(pk=self.att2.pk).exists())

        # As Admin → allowed
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Attendance.objects.filter(pk=self.att2.pk).exists())
