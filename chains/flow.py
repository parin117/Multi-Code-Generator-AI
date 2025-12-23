from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv

load_dotenv() 

llm = ChatGoogleGenerativeAI(model = "gemini-2.0-flash")


flow_prompt =  ChatPromptTemplate.from_messages([
    (
        "system",
        """
            You are a software architect agent.
            Your task is to analyze a user-provided project idea which contains system overview, tech stack and various other things which need to be taken care
            According to that try to generate a clean, modular backend and frontend functionality and feature list.

            Analyse and write the functionality step by step each sub-system needed in for my project idea
            **Note:** 
                - Mention any externel API is needed
                - Mention each and every thing such that programmer just need to code according to it

            You will recieve and thinker agent output which is high level blueprint for the project according to it break down and provide a clean and modular functionalities as an output.

        """
    ),
    ("user", "{thinker_output}")
    # MessagesPlaceholder(variable_name="thinker_output"),
    
])


flow_chain = flow_prompt | llm

# thinker_op = """
#      ## Library Management System Website: Project Blueprint

# **1. PROJECT OVERVIEW**

# *   **Title:** Library Management System Website
# *   **Description:** A comprehensive web-based platform to manage library resources, user accounts, and library operations. This system will cater to various user roles, including librarians, students, and faculty, providing role-specific access and functionalities.
# *   **Objectives:**
#     *   Enable efficient catalog searching and browsing.
#     *   Facilitate user account management (registration, login, profile updates).
#     *   Streamline the borrowing and returning process.
#     *   Provide inventory tracking and management tools for librarians.
#     *   Generate reports on library usage and resource availability.
#     *   Offer a user-friendly and accessible interface for all user types.
# *   **Success Metrics:**
#     *   Increased user engagement (measured by website visits, searches, and borrowing activity).
#     *   Improved efficiency in library operations (reduced checkout/check-in times, faster inventory management).
#     *   High user satisfaction (measured by surveys and feedback).
#     *   Reduced administrative overhead (automated tasks, online reporting).

# **2. TARGET USERS**

# *   **User Groups:**
#     *   **Students:** Primary users for searching the catalog, borrowing and returning books, managing their accounts, and accessing digital resources.
#     *   **Faculty:** Similar access to students, with potential for reserving materials for courses and managing research resources.
#     *   **Librarians:** Administrative users responsible for managing the catalog, user accounts, inventory, borrowing/returning processes, and generating reports.
# *   **Pain Points:**
#     *   **Students/Faculty:** Difficulty finding desired books, long queues for borrowing/returning, limited access to digital resources, inconvenient account management.
#     *   **Librarians:** Time-consuming manual processes, difficulty tracking inventory, inefficient reporting, challenges in managing user accounts.
# *   **User Journeys:**
#     *   **Student:**
#         1.  Logs in to the website.
#         2.  Searches for a book by title, author, or keyword.
#         3.  Views book details (availability, summary, reviews).
#         4.  Checks out the book (if available).
#         5.  Receives email notifications about due dates.
#         6.  Returns the book.
#         7.  Manages their account profile (updates contact information).
#     *   **Librarian:**
#         1.  Logs in to the admin panel.
#         2.  Adds a new book to the catalog.
#         3.  Updates the availability of a book.
#         4.  Manages user accounts (creates, edits, deactivates).
#         5.  Generates a report on overdue books.
#         6.  Processes book returns and check-ins.

# **3. CORE FEATURES**

# *   **Feature Breakdown:**
#     *   **Catalog Search & Browsing (High):** Allows users to search for books and other resources by title, author, ISBN, keyword, etc. Includes advanced search filters and browsing by category.
#     *   **User Account Management (High):** Enables users to register, login, manage their profiles, view borrowing history, and receive notifications.
#     *   **Borrowing & Returning (High):** Facilitates the borrowing and returning of books, including due date tracking, renewals, and late fee management.
#     *   **Inventory Management (High):** Allows librarians to add, edit, and remove books from the catalog, track inventory levels, and manage book locations.
#     *   **Reporting & Analytics (Medium):** Generates reports on library usage, overdue books, popular resources, and other relevant metrics.
#     *   **Digital Resource Access (Medium):** Provides access to e-books, online journals, and other digital resources.
#     *   **Reservation System (Medium):** Allows users to reserve books that are currently checked out.
#     *   **Admin Panel (High):** A dedicated interface for librarians to manage all aspects of the system.
# *   **User Stories:**
#     *   As a student, I want to be able to easily search for books so that I can find the resources I need for my studies.
#     *   As a librarian, I want to be able to quickly add new books to the catalog so that the system is always up-to-date.
#     *   As a librarian, I want to be able to generate reports on overdue books so that I can manage outstanding loans effectively.
#     *   As a student, I want to receive email notifications about upcoming due dates so that I can avoid late fees.

# **4. TECHNICAL ARCHITECTURE**

# *   **Tech Stack:**
#     *   **Frontend:** React (for a dynamic and responsive user interface).
#     *   **Backend:** Node.js with Express.js (for a scalable and efficient server-side application).
#     *   **Database:** PostgreSQL (for reliable data storage and management).
#     *   **Hosting:** AWS or Google Cloud Platform (for scalability and availability).
# *   **System Design:**
#     *   Three-tier architecture: Frontend (React), Backend (Node.js/Express.js), and Database (PostgreSQL).
#     *   RESTful API for communication between the frontend and backend.
#     *   Authentication and authorization using JWT (JSON Web Tokens).
# *   **Integrations:**
#     *   Email service (e.g., SendGrid, Mailgun) for sending notifications.
#     *   Payment gateway (e.g., Stripe, PayPal) for online fee payments (optional).
#     *   Library API (if available) for external data integration.
# *   **Scalability:**
#     *   Horizontal scaling of the backend servers.
#     *   Database replication and sharding.
#     *   Caching mechanisms (e.g., Redis) to improve performance.

# **5. IMPLEMENTATION PLAN**

# *   **Development Phases:**
#     1.  **Phase 1: MVP (Minimum Viable Product)**
#         *   Catalog search and browsing.
#         *   User account management (registration, login, profile).
#         *   Borrowing and returning functionality.
#         *   Admin panel for basic inventory management.
#     2.  **Phase 2: Enhanced Features**
#         *   Reporting and analytics.
#         *   Reservation system.
#         *   Digital resource access.
#         *   Advanced search filters.
#     3.  **Phase 3: Integrations & Optimization**
#         *   Email service integration.
#         *   Payment gateway integration (optional).
#         *   Performance optimization.
#         *   Accessibility improvements.
# *   **MVP Scope:**
#     *   Focus on core functionalities required for basic library operations.
#     *   Simple and intuitive user interface.
#     *   Robust security measures.
# *   **Timelines:**
#     *   Phase 1 (MVP): 8-12 weeks.
#     *   Phase 2: 6-8 weeks.
#     *   Phase 3: 4-6 weeks.
# *   **Resources:**
#     *   Frontend developers (2).
#     *   Backend developers (2).
#     *   Database administrator (1).
#     *   UI/UX designer (1).
#     *   Project manager (1).
#     *   QA tester (1).

# **6. RISKS & MITIGATION**

# *   **Technical Risks:**
#     *   **Scalability issues:** Implement caching and database optimization techniques.
#     *   **Security vulnerabilities:** Conduct regular security audits and penetration testing.
#     *   **Integration c
    
    
#     hallenges:** Thoroughly test integrations with external services.
# *   **Business Risks:**
#     *   **User adoption:** Conduct user training and provide ongoing support.
#     *   **Data migration:** Develop a comprehensive data migration plan.
#     *   **Scope creep:** Clearly define project scope and manage change requests effectively.

# **7. SUCCESS METRICS**

# *   **Key Performance Indicators (KPIs):**
#     *   Number of registered users.
#     *   Website traffic (page views, unique visitors).
#     *   Search query volume.
#     *   Borrowing and returning rates.
#     *   User satisfaction scores.
#     *   Time spent on website.
#     *   Number of overdue books.
# *   **Measurement Criteria:**
#     *   Track website traffic using Google Analytics.
#     *   Monitor user activity through database queries.
#     *   Conduct user surveys to gather feedback.
#     *   Analyze system logs to identify performance bottlenecks.
#     *   Regularly review KPIs to assess project success and identify areas for improvement.
# """
# # print(flow_chain.invoke(thinker_op).content)