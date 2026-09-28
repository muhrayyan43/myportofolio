from __future__ import annotations

import os

from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from main.models import Project


User = get_user_model()

# Fallback passwords let the suite run out of the box; override in .env
# if you want to reuse the same credentials elsewhere (e.g. Burp Suite).
USER_PASSWORD = os.getenv("E2E_USER_PASSWORD", "e2e-user-P@ssw0rd!")
ADMIN_PASSWORD = os.getenv("E2E_ADMIN_PASSWORD", "e2e-admin-P@ssw0rd!")


class BaseE2ETest(StaticLiveServerTestCase):
    """Shared Selenium bootstrap and small helpers."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        options = Options()
        # `--headless=new` uses Chrome's modern headless mode; the extra
        # flags keep it happy inside CI containers and sandboxes.
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1280,900")
        cls.driver = webdriver.Chrome(options=options)
        cls.driver.implicitly_wait(4)
        cls.wait = WebDriverWait(cls.driver, 6)

    @classmethod
    def tearDownClass(cls) -> None:
        try:
            cls.driver.quit()
        finally:
            super().tearDownClass()

    # --- helpers -----------------------------------------------------

    def visit(self, path: str) -> None:
        """Navigate to a path on the live server."""
        self.driver.get(f"{self.live_server_url}{path}")

    def login_via_form(self, username: str, password: str) -> None:
        """Log a user in through the actual login form (not force_login).

        We go through the real UI so the browser stores the session
        cookie and the `last_login` cookie set by `login_user`.
        """
        self.visit(reverse("main:login"))
        self.driver.find_element(By.NAME, "username").send_keys(username)
        self.driver.find_element(By.NAME, "password").send_keys(password)
        self.driver.find_element(
            By.CSS_SELECTOR, "form.auth-form button[type='submit']"
        ).click()
        # After success we are redirected to show_main, where the
        # navbar renders <span class="nav-user">.
        self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".nav-user"))
        )


class AuthFlowTest(BaseE2ETest):
    """Register / login / logout happy paths + validation errors."""

    def test_register_success_redirects_to_login(self) -> None:
        self.visit(reverse("main:register"))

        self.driver.find_element(By.NAME, "username").send_keys("newcomer")
        self.driver.find_element(By.NAME, "password1").send_keys(
            "Sup3rSecret-Password!"
        )
        self.driver.find_element(By.NAME, "password2").send_keys(
            "Sup3rSecret-Password!"
        )
        self.driver.find_element(
            By.CSS_SELECTOR, "form.auth-form button[type='submit']"
        ).click()

        # `register` view redirects to `main:login` and enqueues a
        # success flash message.
        self.wait.until(EC.url_contains("/login/"))
        flash = self.driver.find_element(By.CSS_SELECTOR, ".flash-success")
        self.assertIn("Akun berhasil dibuat", flash.text)

        # The account really exists in the DB now.
        self.assertTrue(User.objects.filter(username="newcomer").exists())

    def test_register_password_mismatch_shows_error(self) -> None:
        self.visit(reverse("main:register"))

        self.driver.find_element(By.NAME, "username").send_keys("mismatched")
        self.driver.find_element(By.NAME, "password1").send_keys(
            "Sup3rSecret-Password!"
        )
        self.driver.find_element(By.NAME, "password2").send_keys(
            "Different-Password!"
        )
        self.driver.find_element(
            By.CSS_SELECTOR, "form.auth-form button[type='submit']"
        ).click()

        # We stay on /register/ and the field-level error is rendered.
        self.assertIn("/register/", self.driver.current_url)
        errors = self.driver.find_elements(By.CSS_SELECTOR, ".form-error")
        self.assertTrue(
            any("password" in e.text.lower() for e in errors),
            "expected a password-related error on the register form",
        )
        self.assertFalse(User.objects.filter(username="mismatched").exists())

    def test_login_wrong_password_shows_error_and_no_cookie(self) -> None:
        User.objects.create_user(username="realuser", password=USER_PASSWORD)

        self.visit(reverse("main:login"))
        self.driver.find_element(By.NAME, "username").send_keys("realuser")
        self.driver.find_element(By.NAME, "password").send_keys("definitely-wrong")
        self.driver.find_element(
            By.CSS_SELECTOR, "form.auth-form button[type='submit']"
        ).click()

        # Still on /login/, no session cookie set, no last_login cookie.
        self.assertIn("/login/", self.driver.current_url)
        self.assertIsNone(self.driver.get_cookie("last_login"))
        self.assertIsNone(self.driver.get_cookie("sessionid"))
        errors = self.driver.find_elements(By.CSS_SELECTOR, ".form-error")
        self.assertGreater(len(errors), 0)

    def test_login_success_sets_last_login_cookie_and_shows_navbar_user(
        self,
    ) -> None:
        User.objects.create_user(username="realuser", password=USER_PASSWORD)

        self.login_via_form("realuser", USER_PASSWORD)

        # Redirected to the home page, navbar now shows the username.
        nav_user = self.driver.find_element(By.CSS_SELECTOR, ".nav-user")
        self.assertIn("realuser", nav_user.text)

        # `login_user` sets a last_login cookie whose value is the
        # human-readable "YYYY-MM-DD HH:MM:SS" timestamp.
        last_login = self.driver.get_cookie("last_login")
        self.assertIsNotNone(last_login, "last_login cookie should be set")
        self.assertRegex(
            last_login["value"], r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$"
        )

        # The home page also renders it under "Sesi Terakhir Login".
        self.assertIn("Sesi Terakhir Login", self.driver.page_source)

    def test_logout_clears_last_login_cookie_and_hides_username(self) -> None:
        User.objects.create_user(username="realuser", password=USER_PASSWORD)
        self.login_via_form("realuser", USER_PASSWORD)

        self.driver.find_element(
            By.CSS_SELECTOR, "a.nav-cta-logout"
        ).click()

        # After logout the navbar reverts to Login / Register — and
        # crucially the last_login cookie is gone.
        self.wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "a.nav-cta-primary")  # Register button
            )
        )
        self.assertIsNone(self.driver.get_cookie("last_login"))
        with self.assertRaises(NoSuchElementException):
            self.driver.find_element(By.CSS_SELECTOR, ".nav-user")


class AuthorizationTest(BaseE2ETest):
    """Three-role check on create_project: visitor / user / superuser."""

    def setUp(self) -> None:
        super().setUp()
        self.regular_user = User.objects.create_user(
            username="regular_e2e", password=USER_PASSWORD
        )
        self.admin_user = User.objects.create_superuser(
            username="admin_e2e", password=ADMIN_PASSWORD
        )

    def test_visitor_is_redirected_to_login_with_next(self) -> None:
        # Anonymous visit to a protected page → @login_required kicks
        # in and redirects to /login/?next=/project/create/.
        self.visit(reverse("main:create_project"))
        self.wait.until(EC.url_contains("/login/"))
        self.assertIn("next=", self.driver.current_url)
        self.assertIn("%2Fproject%2Fcreate%2F", self.driver.current_url)

    def test_regular_user_gets_403_forbidden(self) -> None:
        self.login_via_form("regular_e2e", USER_PASSWORD)
        self.visit(reverse("main:create_project"))
        # PermissionDenied → Django renders the 403 debug page in DEBUG.
        self.assertIn("403", self.driver.title + self.driver.page_source)

    def test_superuser_sees_create_project_form(self) -> None:
        self.login_via_form("admin_e2e", ADMIN_PASSWORD)
        self.visit(reverse("main:create_project"))
        # The project form has a Nama Proyek input rendered from
        # ProjectForm; its presence proves the page loaded successfully.
        self.assertNotIn("403", self.driver.title)
        self.driver.find_element(By.NAME, "title")


class StarToggleTest(BaseE2ETest):
    """Star / unstar for a logged-in regular user."""

    def setUp(self) -> None:
        super().setUp()
        self.user = User.objects.create_user(
            username="star_e2e", password=USER_PASSWORD
        )
        self.project = Project.objects.create(
            title="Selenium Star Target",
            description="Project used by the E2E star toggle test.",
            tech_stack="Django, Selenium",
            year=2026,
        )

    def _star_count_for(self, project_id: int) -> int:
        """Read the numeric star count next to the button we care about."""
        button = self.driver.find_element(
            By.CSS_SELECTOR,
            f"form.star-form[action$='/project/{project_id}/star/'] "
            "button.button-star",
        )
        return int(button.find_element(By.CSS_SELECTOR, ".star-count").text)

    def test_star_toggle_increments_then_decrements_count(self) -> None:
        self.login_via_form("star_e2e", USER_PASSWORD)
        self.visit(reverse("main:show_project"))

        self.assertEqual(self._star_count_for(self.project.id), 0)

        # Star it.
        self.driver.find_element(
            By.CSS_SELECTOR,
            f"form.star-form[action$='/project/{self.project.id}/star/'] "
            "button.button-star",
        ).click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (
                    By.CSS_SELECTOR,
                    f"form.star-form[action$='/project/{self.project.id}/star/'] "
                    ".star-count",
                ),
                "1",
            )
        )
        self.assertIn(
            self.user, self.project.starred_by.all(),
            "user should be recorded in starred_by after starring",
        )

        # Unstar it.
        self.driver.find_element(
            By.CSS_SELECTOR,
            f"form.star-form[action$='/project/{self.project.id}/star/'] "
            "button.button-star",
        ).click()
        self.wait.until(
            EC.text_to_be_present_in_element(
                (
                    By.CSS_SELECTOR,
                    f"form.star-form[action$='/project/{self.project.id}/star/'] "
                    ".star-count",
                ),
                "0",
            )
        )
        self.assertNotIn(self.user, self.project.starred_by.all())