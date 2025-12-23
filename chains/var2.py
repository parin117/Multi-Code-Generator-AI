# flow = """
# Of course. As a software architect, I will break down the provided project blueprint into a detailed and modular list of functionalities for both the backend and frontend. This guide is structured to allow a programmer to begin development directly.

# ---

# ### External API Requirements

# *   **None.** This project is self-contained and does not require any third-party APIs for its core functionality.

# ---

# ## Backend Functionality (Node.js with Express)

# The backend will serve as a RESTful API to handle all data operations for the TODO items.

# ### 1. Database Setup (SQLite)

# *   **Action:** Create a database file (e.g., `todos.db`).
# *   **Action:** Create a table named `todos`.
# *   **Table Schema (`todos`):**
#     *   `id`: INTEGER, PRIMARY KEY, AUTOINCREMENT
#     *   `description`: TEXT, NOT NULL (Cannot be empty)
#     *   `category`: TEXT, NOT NULL
#     *   `due_date`: TEXT (Store as ISO 8601 string: `YYYY-MM-DD`)
#     *   `priority`: TEXT, NOT NULL (e.g., 'Low', 'Medium', 'High')
#     *   `is_completed`: INTEGER, NOT NULL, DEFAULT 0 (Use 0 for false, 1 for true)
#     *   `created_at`: DATETIME, DEFAULT CURRENT_TIMESTAMP
#     *   `updated_at`: DATETIME, DEFAULT CURRENT_TIMESTAMP
# *   **Action:** Create database indexes on `category`, `due_date`, and `priority` columns to speed up filtering queries.

# ### 2. API Endpoints (RESTful)

# This section defines the contract between the frontend and backend. All responses should be in JSON format.

# #### **Endpoint: `GET /api/todos`**
# *   **Purpose:** Fetch a list of all TODO items.
# *   **Functionality:**
#     1.  Query the `todos` table for all records.
#     2.  Implement filtering based on optional query parameters:
#         *   `category` (e.g., `/api/todos?category=Work`)
#         *   `priority` (e.g., `/api/todos?priority=High`)
#         *   `due_date` (e.g., `/api/todos?due_date=2024-12-25`)
#     3.  The logic should combine filters if multiple are provided (e.g., `.../?category=Work&priority=High`).
#     4.  Order the results by `due_date` in ascending order.
# *   **Success Response (200 OK):**
#     *   Body: An array of TODO objects. `[{"id": 1, "description": "...", ...}, ...]`
# *   **Error Response (500 Internal Server Error):**
#     *   Body: `{"error": "Failed to fetch TODOs"}`

# #### **Endpoint: `POST /api/todos`**
# *   **Purpose:** Create a new TODO item.
# *   **Functionality:**
#     1.  Receive TODO data from the request body (`description`, `category`, `due_date`, `priority`).
#     2.  Perform data validation (see section 3).
#     3.  If validation fails, return a 400 Bad Request error.
#     4.  If validation passes, insert a new record into the `todos` table. `is_completed` should default to `0` (false).
# *   **Request Body:**
#     *   `{"description": "...", "category": "...", "due_date": "...", "priority": "..."}`
# *   **Success Response (201 Created):**
#     *   Body: The newly created TODO object, including its `id`. `{"id": 2, "description": "...", ...}`
# *   **Error Response (400 Bad Request):**
#     *   Body: `{"error": "Description cannot be empty."}` (or other validation messages).

# #### **Endpoint: `PUT /api/todos/:id`**
# *   **Purpose:** Update an existing TODO item. Can be used for editing content or marking it as complete.
# *   **Functionality:**
#     1.  Find the TODO by its `id` from the URL parameter.
#     2.  If not found, return a 404 Not Found error.
#     3.  Receive updated data from the request body. The body can contain any subset of the fields: `description`, `category`, `due_date`, `priority`, `is_completed`.
#     4.  Perform validation on the received fields.
#     5.  Update the corresponding record in the `todos` table. Also, update the `updated_at` timestamp.
# *   **Request Body (Example):**
#     *   `{"priority": "High", "is_completed": 1}`
# *   **Success Response (200 OK):**
#     *   Body: The fully updated TODO object. `{"id": 1, "description": "...", "priority": "High", ...}`
# *   **Error Response (404 Not Found):**
#     *   Body: `{"error": "TODO item not found."}`

# #### **Endpoint: `DELETE /api/todos/:id`**
# *   **Purpose:** Delete a TODO item.
# *   **Functionality:**
#     1.  Find the TODO by its `id` from the URL parameter.
#     2.  If not found, return a 404 Not Found error.
#     3.  Delete the record from the `todos` table.
# *   **Success Response (204 No Content):**
#     *   Return no body content, only the status code.
# *   **Error Response (404 Not Found):**
#     *   Body: `{"error": "TODO item not found."}`

# ### 3. Data Validation and Business Logic

# *   **Location:** This logic should be implemented as middleware in Express before the main controller logic for `POST` and `PUT` routes.
# *   **Validation Rules:**
#     *   `description`: Must be a non-empty string.
#     *   `category`: Must be a non-empty string.
#     *   `due_date`: Must be a valid date string in `YYYY-MM-DD` format.
#     *   `priority`: Must be one of 'Low', 'Medium', or 'High'.
#     *   `is_completed`: (On `PUT` requests) Must be a boolean or integer (0 or 1).
# *   **Security:** Sanitize all string inputs to prevent basic XSS or SQL injection attacks, even though SQLite has good parameter binding protection.

# ---

# ## Frontend Functionality (React)

# The frontend is a single-page application (SPA) responsible for all user interaction and rendering.

# ### 1. Component Breakdown

# #### **`App.js` (Root Component)**
# *   **Purpose:** The main entry point of the application.
# *   **Functionality:**
#     *   Renders the main layout, including a title header.
#     *   Renders the `Dashboard` component.

# #### **`Dashboard.js`**
# *   **Purpose:** The primary container that orchestrates the main UI elements.
# *   **State Management:**
#     *   `todos` (Array): Stores the list of all TODO items fetched from the API.
#     *   `filteredTodos` (Array): Stores the list of todos to be displayed after filtering.
#     *   `isLoading` (Boolean): Tracks if an API call is in progress to show a loading indicator.
#     *   `error` (String/null): Stores any error messages from API calls.
# *   **Functionality:**
#     1.  **Fetch Todos:** Use a `useEffect` hook to call the `GET /api/todos` endpoint when the component mounts.
#     2.  **State Updates:** Update the `todos` and `filteredTodos` state with the fetched data. Set `isLoading` to `false`.
#     3.  **Handler Functions:** Define functions to handle creating, updating, and deleting todos. These functions will make the API calls and then update the local `todos` state to reflect the change immediately, providing a fast UX.
#         *   `handleAddTask(newTodoData)`
#         *   `handleDeleteTask(todoId)`
#         *   `handleUpdateTask(todoId, updatedData)`
#         *   `handleFilterChange(filterCriteria)`
#     4.  **Render Child Components:**
#         *   Render `<FilterControls>` and pass `handleFilterChange` as a prop.
#         *   Render `<AddTodoForm>` and pass `handleAddTask` as a prop.
#         *   Render `<TodoList>` and pass `filteredTodos`, `handleDeleteTask`, and `handleUpdateTask` as props.

# #### **`FilterControls.js`**
# *   **Purpose:** Allow the user to filter the visible TODO list.
# *   **Props:**
#     *   `onFilterChange(filterCriteria)`: A function to call when a filter is changed.
# *   **Functionality:**
#     *   Render dropdowns (`<select>`) or radio buttons for:
#         *   **Category:** Populate options dynamically from the fetched todos or use a predefined list.
#         *   **Priority:** ('All', 'Low', 'Medium', 'High').
#         *   **Due Date:** Could be a date picker input `<input type="date">`.
#     *   When any filter value changes, construct a `filterCriteria` object (e.g., `{ category: 'Work', priority: 'All' }`) and call the `onFilterChange` prop.
#     *   Include a "Clear Filters" button to reset all filters.

# #### **`AddTodoForm.js`**
# *   **Purpose:** A form for creating new TODO items.
# *   **Props:**
#     *   `onAddTask(newTodoData)`: A function to call when the form is submitted.
# *   **State Management:**
#     *   Local state for each input field: `description`, `category`, `dueDate`, `priority`.
# *   **Functionality:**
#     *   Render a `<form>` element.
#     *   Render input fields:
#         *   Description: `<input type="text">`
#         *   Category: `<input type="text">`
#         *   Due Date: `<input type="date">`
#         *   Priority: `<select>` with 'Low', 'Medium', 'High' options.
#     *   On form submission:
#         1.  Prevent the default form submission event.
#         2.  Perform basic client-side validation (e.g., description is not empty).
#         3.  Call the `onAddTask` prop with the form data.
#         4.  Clear the form fields after successful submission.

# #### **`TodoList.js`**
# *   **Purpose:** Display the list of TODO items.
# *   **Props:**
#     *   `todos` (Array): The list of todos to display.
#     *   `onDeleteTask(todoId)`
#     *   `onUpdateTask(todoId, updatedData)`
# *   **Functionality:**
#     *   If `todos` array is empty, display a message like "No tasks found. Add one above!".
#     *   Map over the `todos` array and render a `<TodoItem>` component for each item.
#     *   Pass the individual `todo` object and the handler functions (`onDeleteTask`, `onUpdateTask`) as props to each `<TodoItem>`.

# #### **`TodoItem.js`**
# *   **Purpose:** Display a single TODO item and its controls.
# *   **Props:**
#     *   `todo` (Object): The specific TODO item's data.
#     *   `onDeleteTask(todoId)`
#     *   `onUpdateTask(todoId, updatedData)`
# *   **Functionality:**
#     *   Render the details of the `todo` object: `description`, `category`, `due_date`, `priority`.
#     *   Apply a visual style (e.g., a strikethrough) if `todo.is_completed` is true.
#     *   Render a checkbox (`<input type="checkbox">`):
#         *   Its `checked` status is bound to `todo.is_completed`.
#         *   `onChange`, it calls `onUpdateTask(todo.id, { is_completed: !todo.is_completed })`.
#     *   Render a "Delete" button:
#         *   `onClick`, it calls `onDeleteTask(todo.id)`.
#     *   Render an "Edit" button:
#         *   `onClick`, this would ideally open a modal (`<EditTodoModal>`) for a better user experience, pre-filled with the current `todo` data. For a simpler implementation, it could transform the item into an editable form in-place.

# #### **`EditTodoModal.js` (Optional but Recommended)**
# *   **Purpose:** A modal dialog for editing an existing task.
# *   **Props:**
#     *   `todo` (Object): The task being edited.
#     *   `onUpdate(updatedData)`: Function to call with the new data.
#     *   `onClose()`: Function to close the modal.
# *   **Functionality:**
#     *   A form pre-filled with the data from the `todo` prop.
#     *   On submit, it calls the `onUpdate` prop.
#     *   Has "Save" and "Cancel" buttons. The cancel button calls `onClose`.

# """

flow = """
**I. BACKEND FUNCTIONALITY (API)**

*   **Technology:** Node.js with Express.js (as per your tech stack)
*   **Database:** MongoDB (as per your tech stack)
*   **Core Modules:**
    *   Authentication and Authorization
    *   Content Management
    *   User Management (Admin Users)
    *   Error Handling and Logging

**A. Authentication and Authorization Module**

1.  **Functionality:**
    *   **Admin User Registration:**
        *   Endpoint: `POST /api/admin/register`
        *   Functionality: Create a new admin user account.
        *   Input: `username`, `email`, `password`
        *   Validation:
            *   Check if the username/email already exists.
            *   Password complexity validation.
        *   Action:
            *   Hash the password using bcrypt or similar.
            *   Store the user in the database with `username`, `email`, `hashedPassword`, `role` (set to "admin").
            *   Return success message.
        *   Error Handling:
            *   Return appropriate error messages for invalid input or database errors.

    *   **Admin User Login:**
        *   Endpoint: `POST /api/admin/login`
        *   Functionality: Log in an existing admin user.
        *   Input: `username` or `email`, `password`
        *   Validation:
            *   Check if the user exists in the database.
            *   Compare the provided password with the stored hashed password.
        *   Action:
            *   If credentials are valid, generate a JSON Web Token (JWT).
            *   Return the JWT to the client.
        *   Error Handling:
            *   Return appropriate error messages for invalid credentials.

    *   **Authentication Middleware:**
        *   Functionality: Protect API endpoints that require admin access.
        *   Action:
            *   Extract the JWT from the `Authorization` header.
            *   Verify the JWT's signature.
            *   Decode the JWT to get the user's ID.
            *   Fetch the user from the database.
            *   Attach the user object to the request object (`req.user`).
            *   Call `next()` to proceed to the next middleware or route handler.
        *   Error Handling:
            *   Return a 401 Unauthorized error if the JWT is invalid or missing.
            *   Return a 403 Forbidden error if the user doesn't have the required role.

**B. Content Management Module**

1.  **Hero Section:**
    *   Model: `Hero` (fields: `title`, `subtitle`, `imageURL`, `buttonText`, `buttonLink`)
    *   Endpoints:
        *   `GET /api/hero`:  Retrieve the hero section data.
        *   `PUT /api/hero`:  Update the hero section data (requires admin authentication).
            *   Input: JSON object with fields to update.
            *   Validation: Validate input data types and required fields.
            *   Action: Update the `Hero` document in the database.

2.  **Education Section:**
    *   Model: `Education` (fields: `degree`, `institution`, `year`, `description`)
    *   Endpoints:
        *   `GET /api/education`: Retrieve all education entries.
        *   `POST /api/education`: Create a new education entry (requires admin authentication).
            *   Input: JSON object with education details.
            *   Validation: Validate input data.
            *   Action: Create a new `Education` document in the database.
        *   `GET /api/education/:id`: Retrieve a specific education entry by ID.
        *   `PUT /api/education/:id`: Update an education entry by ID (requires admin authentication).
        *   `DELETE /api/education/:id`: Delete an education entry by ID (requires admin authentication).

3.  **Certifications Section:**
    *   Model: `Certification` (fields: `name`, `authority`, `date`, `credentialURL`)
    *   Endpoints: Similar to Education Section (GET, POST, GET/:id, PUT/:id, DELETE/:id).

4.  **Coding Profile Section:**
    *   Model: `CodingProfile` (fields: `githubURL`, `stackOverflowURL`, `otherPlatforms`)
    *   Endpoints:
        *   `GET /api/coding-profile`: Retrieve the coding profile data.
        *   `PUT /api/coding-profile`: Update the coding profile data (requires admin authentication).

5.  **Projects Section:**
    *   Model: `Project` (fields: `title`, `description`, `imageURL`, `technologies`, `liveDemoURL`, `githubURL`)
    *   Endpoints: Similar to Education Section (GET, POST, GET/:id, PUT/:id, DELETE/:id).

6.  **Contact Section:**
    *   Model: `Contact` (fields: `email`, `phone`, `address`, `linkedinURL`, `githubURL`)
    *   Endpoints:
        *   `GET /api/contact`: Retrieve contact details.
        *   `PUT /api/contact`: Update contact details (requires admin authentication).

7.  **Contact Form Submissions:**
    *   Model: `Submission` (fields: `name`, `email`, `message`, `timestamp`)
    *   Endpoints:
        *   `POST /api/submit`:  Receive a new contact form submission.
            *   Input: `name`, `email`, `message`
            *   Validation: Validate email format, required fields.
            *   Action:
                *   Save the submission to the database.
                *   **Send an email notification** to the admin using a service like Nodemailer or SendGrid (External API).
        *   `GET /api/submissions`: Retrieve all contact form submissions (requires admin authentication).
        *   `GET /api/submissions/:id`: Retrieve a specific submission by ID (requires admin authentication).
        *   `DELETE /api/submissions/:id`: Delete a submission by ID (requires admin authentication).

**C. User Management Module (Admin Users)**

*   **Functionality:** (Beyond the initial registration in the Authentication Module)
    *   List Admin Users: `GET /api/admin/users` (requires admin authentication)
    *   Delete Admin User: `DELETE /api/admin/users/:id` (requires admin authentication, potentially with role-based access control to prevent deleting the primary admin).

**D. Error Handling and Logging**

*   Implement global error handling middleware to catch errors and return appropriate error responses to the client.
*   Use a logging library like Winston or Morgan to log API requests, errors, and other important events.

**II. FRONTEND FUNCTIONALITY (Portfolio Website & Admin Dashboard)**

*   **Technology:** React (as per your tech stack)

**A. Portfolio Website (Public View)**

1.  **Components:**
    *   `Hero`: Displays hero section data fetched from `/api/hero`.
    *   `EducationList`: Displays a list of education entries fetched from `/api/education`.
    *   `CertificationList`: Displays a list of certifications fetched from `/api/certifications`.
    *   `CodingProfile`: Displays coding profile data fetched from `/api/coding-profile`.
        *   Consider using iframes or links to external profiles (GitHub, Stack Overflow).
    *   `ProjectList`: Displays a list of projects fetched from `/api/projects`.
    *   `ContactForm`:
        *   Allows users to submit contact information.
        *   On submit, sends data to `POST /api/submit`.
        *   Displays success/error messages to the user.
    *   `ContactDetails`: Displays contact details fetched from `/api/contact`.
    *   `Footer`: Contains copyright information and links.
    *   `Navigation`: Main navigation bar.

2.  **Functionality:**
    *   Fetch data from the backend API on component mount.
    *   Display data in a visually appealing and responsive manner.
    *   Handle form submissions and display appropriate feedback.
    *   Implement client-side routing using React Router.
    *   SEO optimization (using libraries like React Helmet).

**B. Admin Dashboard**

1.  **Components:**
    *   `Login`:  Handles admin user login.
        *   Sends credentials to `POST /api/admin/login`.
        *   Stores the JWT in local storage or a cookie upon successful login.
        *   Redirects to the main dashboard page.
    *   `Dashboard`:  Main dashboard component (protected by authentication).
        *   Displays an overview of the website content.
        *   Provides links to manage each section (Hero, Education, Certifications, etc.).
    *   `HeroEditor`:  Allows admins to edit the hero section data.
        *   Fetches data from `/api/hero`.
        *   Sends updates to `PUT /api/hero`.
    *   `EducationManager`:  Allows admins to create, edit, and delete education entries.
        *   Fetches data from `/api/education`.
        *   Uses `POST`, `PUT`, and `DELETE` requests to manage education entries.
    *   `CertificationManager`: Similar to `EducationManager` for certifications.
    *   `CodingProfileEditor`: Allows admins to edit the coding profile data.
    *   `ProjectManager`: Similar to `EducationManager` for projects.
    *   `ContactEditor`: Allows admins to edit the contact details.
    *   `SubmissionList`: Displays a list of contact form submissions.
        *   Fetches data from `/api/submissions`.
        *   Allows admins to view and delete submissions.
    *   `AdminUserList`: Display list of admin users
        *   Fetches data from `/api/admin/users`.
        *   Allows admins to delete users

2.  **Functionality:**
    *   Implement authentication using the JWT stored in local storage or a cookie.
    *   Use React Router to navigate between different sections of the dashboard.
    *   Fetch data from the backend API and display it in editable forms.
    *   Send updates to the backend API using `PUT`, `POST`, and `DELETE` requests.
    *   Implement form validation to ensure data integrity.
    *   Display success/error messages to the user.

**III. EXTERNAL API INTEGRATIONS**

1.  **Email Service (for Contact Form Submissions):**
    *   Nodemailer (for direct email sending from the backend) - requires configuring an email account.
    *   SendGrid, Mailgun, or AWS SES (for more reliable email delivery, especially in production).
    *   API Key: Required for authentication.
    *   Functionality: Send an email to the admin when a new contact form submission is received.

2.  **GitHub/Stack Overflow API (Optional - for richer Coding Profile):**
    *   GitHub API: Fetch user's repositories, contributions, etc.
        *   API Key: May be required for higher rate limits.
    *   Stack Overflow API: Fetch user's reputation, badges, etc.
        *   API Key: May be required.
    *   Functionality: Display more detailed information about the user's coding activity.

**IV. DATABASE DESIGN (MongoDB)**

*   **Collections:**
    *   `admins`: Stores admin user credentials (username, email, hashedPassword, role).
    *   `hero`: Stores hero section data (single document).
    *   `education`: Stores education entries (multiple documents).
    *   `certifications`: Stores certification entries (multiple documents).
    *   `codingProfile`: Stores coding profile data (single document).
    *   `projects`: Stores project entries (multiple documents).
    *   `contact`: Stores contact details (single document).
    *   `submissions`: Stores contact form submissions (multiple documents).

**V. KEY CONSIDERATIONS**

*   **Security:**  Prioritize security throughout the development process.  Use HTTPS, validate all input, sanitize data, and protect against common web vulnerabilities.  Regular security audits are essential.
*   **Scalability:**  Design the backend API and database to handle increased traffic.  Consider using caching, load balancing, and database optimization techniques.
*   **Maintainability:**  Write clean, modular code with clear documentation.  Use a consistent coding style and follow best practices.
*   **Testing:**  Implement thorough unit tests, integration tests, and end-to-end tests to ensure the quality of the code.
*   **Deployment:**  Automate the deployment process using CI/CD pipelines.

This detailed breakdown should provide a solid foundation for your developers to build the portfolio website and admin dashboard. Remember to communicate clearly and frequently throughout the development process. Good luck!
"""

design_config = """
### 🎨 **1. Color Scheme**

#### **Primary Palette**

* `#1E90FF` - Primary Buttons, CTA Links, Highlights
* `#0F62FE` - Secondary Buttons, Interactive Icons
* `#1A1A1A` - Main Text, Strong Emphasis (Light Mode)
* `#F4F4F4` - Background Surface, Light Containers
* `#FFFFFF` - Base Background, High Contrast Elements

#### **Accent & Interaction Colors**

* `#3DDC97` - Hover State (Buttons, Interactive Links)
* `#28B485` - Focus / Active State Borders and Shadows
* `#F8D210` - Warning/Alert Highlights
* `#E63946` - Error / Destructive Actions

#### **Backgrounds**

* `#F9FAFB` - Default Light Background
* `#0D1117` - Default Dark Background
* `rgba(255, 255, 255, 0.05)` - Surface Overlay (Dark Glassmorphism)
* `rgba(255, 255, 255, 0.85)` - Modal/Card Surface (Light Translucency)

#### **Typography Colors**

* `#111827` - Primary Text (Light Mode)
* `#E5E7EB` - Primary Text (Dark Mode)
* `#6B7280` - Secondary Text (Light Mode)
* `#9CA3AF` - Secondary Text (Dark Mode)

---

### ✨ **Shadows & Depth**

* **Light Mode Shadow:**
  `0px 4px 12px rgba(0, 0, 0, 0.06)`
* **Dark Mode Shadow:**
  `0px 4px 12px rgba(255, 255, 255, 0.05)`

---

### 🧠 **Visual Intent**

* Subtle depth using soft shadows and transparency.
* Components should feel tactile, slightly raised (neumorphic inspiration).
* Avoid harsh gradients or high-contrast outlines unless for alerts or focus rings.

"""

# design_config = """
# Okay, based on the provided application flow for the TODO application, here's a design configuration for the front-end engineer, focusing on visual appeal and contemporary aesthetics:

# ## Design Configuration: TODO Application

# This document outlines the visual design specifications for the TODO application's front-end.  It aims for a clean, modern, and user-friendly experience.

# **I. Overall Aesthetic:**

# *   **Style:** Minimalist and clean with subtle use of neumorphism/glassmorphism for depth and visual interest. The goal is to be modern, approachable, and not visually overwhelming.
# *   **Focus:** Prioritize readability and ease of use.  Information should be clearly presented and easily scannable.
# *   **Responsiveness:** The design must be fully responsive and adapt seamlessly to different screen sizes (desktop, tablet, mobile).

# **II. Color Scheme:**

# *   **Primary Color:** `#6366F1` (Indigo-500 from Tailwind CSS palette).  This will be used for primary actions, buttons, and highlights.
# *   **Secondary Color:** `#A78BFA` (Indigo-300 from Tailwind CSS palette).  Use this for secondary actions, hover states, and subtle accents.
# *   **Background Color:** `#F9FAFB` (Gray-50 from Tailwind CSS palette).  A very light gray to provide a subtle contrast against the content.
# *   **Surface Color:** `#FFFFFF` (White).  Used for cards, modals, and other containers to create visual separation.  Consider a very subtle box-shadow for depth.
# *   **Text Color (Primary):** `#1E293B` (Gray-800 from Tailwind CSS palette).  Dark gray for primary text content.
# *   **Text Color (Secondary):** `#4B5563` (Gray-600 from Tailwind CSS palette).  Medium gray for less important text, labels, and descriptions.
# *   **Accent Color (Priority - Low):** `#22C55E` (Green-500 from Tailwind CSS palette).
# *   **Accent Color (Priority - Medium):** `#F59E0B` (Amber-500 from Tailwind CSS palette).
# *   **Accent Color (Priority - High):** `#EF4444` (Red-500 from Tailwind CSS palette).
# *   **Error Color:** `#DC2626` (Red-600 from Tailwind CSS palette).  For error messages and validation feedback.
# *   **Success Color:** `#16A34A` (Green-600 from Tailwind CSS palette). For success messages and validation feedback.

# **III. Font Configuration:**

# *   **Font Family:**  "Inter", sans-serif (or "Roboto", sans-serif as a fallback if Inter is not available).  This font is clean, modern, and highly readable.
# *   **Font Weights:**
#     *   **Regular (400):** For body text and general content.
#     *   **Medium (500):** For headings, labels, and important text.
#     *   **Semi-Bold (600):** For strong emphasis and call-to-actions.
# *   **Font Sizes:** (These are guidelines, adjust as needed for responsiveness)
#     *   **H1 (Main Title):** 36px (2.25rem)
#     *   **H2 (Section Titles):** 24px (1.5rem)
#     *   **H3 (Sub-section Titles):** 20px (1.25rem)
#     *   **Body Text:** 16px (1rem)
#     *   **Small Text (Labels, Captions):** 14px (0.875rem)
# *   **Line Height:** 1.5 for body text to improve readability.
# *   **Letter Spacing:** Normal (0) for most text.  Consider slightly increased letter spacing (0.025em) for headings to enhance visual appeal.

# **IV. Component-Specific Design:**

# *   **AddTodoForm:**
#     *   Input fields should have rounded corners (8px radius).
#     *   Use a subtle box-shadow for the form container to create a sense of depth.
#     *   The "Add Task" button should use the primary color (`#6366F1`) and have a hover state that lightens the color.
# *   **FilterControls:**
#     *   Use visually distinct dropdowns/select elements for category and priority.
#     *   The date picker should be easily accessible and intuitive to use.
#     *   The "Clear Filters" button should be a secondary button style (e.g., outlined).
# *   **TodoList:**
#     *   Each `TodoItem` should be displayed in a card-like container with rounded corners (8px radius) and a subtle box-shadow.
#     *   Use clear visual cues to indicate the priority of each task (e.g., colored borders or icons).
#     *   Completed tasks should have a visual indication (e.g., strikethrough text, faded color).
# *   **TodoItem:**
#     *   The checkbox for marking a task as complete should be visually prominent and easy to interact with.
#     *   The "Delete" button should use a subtle icon (e.g., a trash can) and a confirmation dialog to prevent accidental deletions.
#     *   The "Edit" button (if implemented as an in-place form) should provide clear visual feedback when the item is being edited.
# *   **EditTodoModal (Optional):**
#     *   The modal should have a semi-transparent backdrop to focus the user's attention.
#     *   The form within the modal should follow the same design principles as the `AddTodoForm`.
#     *   Use clear "Save" and "Cancel" buttons.

# **V. Effects and Animations:**

# *   **Hover Effects:** Use subtle hover effects (e.g., slight color changes, increased box-shadow) to provide feedback to the user.
# *   **Transitions:** Use smooth transitions (e.g., 0.2s duration) for state changes and animations to create a polished user experience.
# *   **Loading Indicator:** Use a visually appealing loading indicator (e.g., a spinner or progress bar) while data is being fetched from the API.

# **VI. Accessibility:**

# *   **Color Contrast:** Ensure sufficient color contrast between text and background colors to meet accessibility guidelines (WCAG).
# *   **Keyboard Navigation:** Ensure that all interactive elements can be accessed and used via keyboard navigation.
# *   **Screen Reader Compatibility:** Use semantic HTML and ARIA attributes to ensure that the application is accessible to screen readers.

# **VII. Glassmorphism/Neumorphism Considerations:**

# *   **Subtlety is Key:**  Avoid overusing these effects.  They should be used sparingly to add depth and visual interest without sacrificing readability or usability.
# *   **Glassmorphism:**  Apply a subtle frosted glass effect to containers (e.g., cards, modals) by using a semi-transparent background color and a blur filter.  Ensure sufficient contrast for text on top of the blurred background.
# *   **Neumorphism:**  Use very subtle box-shadows to create the illusion of raised or recessed elements.  Avoid using strong shadows that can make the UI look dated.

# **VIII. Iconography:**

# *   **Style:** Use a consistent icon style (e.g., outline icons from Font Awesome or Material Design Icons).
# *   **Size:** Choose icon sizes that are appropriate for the context (e.g., 16px or 20px for buttons, 24px or 32px for larger elements).
# *   **Color:** Use the primary or secondary color for icons, depending on their importance.

# **IX. Example Implementation Notes (Tailwind CSS):**

# This configuration is designed to be easily implemented using a utility-first CSS framework like Tailwind CSS. Here are some examples:

# *   **Background Color:** `<div className="bg-gray-50">...</div>`
# *   **Text Color:** `<p className="text-gray-800">...</p>`
# *   **Primary Button:** `<button className="bg-indigo-500 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded">...</button>`
# *   **Card:** `<div className="bg-white rounded-lg shadow-md p-4">...</div>`
# *   **Glassmorphism:** `<div className="bg-white/20 backdrop-blur-md rounded-lg p-4">...</div>`
# *   **Neumorphism:** `<div className="bg-gray-100 rounded-lg shadow-inner shadow-gray-300">...</div>`

# This design configuration provides a solid foundation for creating a visually appealing and user-friendly TODO application.  Remember to iterate and refine the design based on user feedback and testing. Good luck!
# """

root_path = "/Users/aaryagopani/Downloads/Multi_Code_Gen_Practice/practice"
Directory = {
}