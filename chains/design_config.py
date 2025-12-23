from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

design_prompt = PromptTemplate(
    template="""
You are an expert UI/UX designer specializing in modern web applications. Your role is to create a complete, highly detailed **visual design configuration** that frontend engineers can implement directly.

---

🎯 **OBJECTIVE**:  
Analyze the application flow below and return only the **visual styling configuration**, focused on colors, font families, and visual effects (glassmorphism + subtle neumorphism). Avoid layout, component sizing, or implementation code.

---

🔷 **REQUIRED OUTPUT SECTIONS** (MANDATORY, DO NOT OMIT):

---

**1. Color Scheme**:
- Provide a beautiful, modern, and cohesive palette with hex codes.
- For each color, specify its exact intended usage (e.g., "Primary Button Background", "Card Surface", "Error State").
- Include:
  - **Primary Color Palette** (3-5 colors): Buttons, tabs, links, key highlights.
  - **Accent / Interaction Colors**: Hover, active, focus states.
  - **Background Colors**: Page background, card/modal surfaces; include both light and dark mode if applicable.
  - **Text Colors**: Primary, secondary, muted, with usage notes.
  - **State Colors**: Success, Warning, Error — visually distinct and accessible.

---

**2. Font Configuration**:
- Choose clean, modern, web-safe fonts.
- For each font, specify where and how to use it.
- Include:
  - **Primary Font Family**: For most text (with fallback options).
  - **Secondary Font Family** (Optional): For large headings or brand identity.
  - **Font Weights**: Recommend usage for light, regular, medium, bold (e.g., "500 - Buttons", "700 - H1, H2").

---

**3. Glassmorphism Configuration**:
- Define exactly how to use glassmorphism across the UI.
- Include:
  - **Backdrop Blur Intensity** (in px)
  - **Background Opacity** (in %)
  - **Border Style** (color, thickness, opacity)
  - **Shadow Style** (e.g., soft white/black outer shadow)
  - **Recommended Usage**: Where to apply glassmorphism (cards, modals, navbars, etc.)
  - **Layering**: Which glass elements sit above/below others for depth

---

**4. Neumorphism Guidelines**:
- Use only where it visually enhances depth (subtle, not dominant).
- Include:
  - **Recommended Usage**: Toggle switches, small buttons, cards (only if helpful)
  - **Shadow Style**: Light + dark dual shadows, inset/extruded, light direction
  - **Visual Intention**: Should the element look soft-pressed, raised, or tactile?

---

🔒 **DESIGN STYLE CONSTRAINTS**:
- Modern, clean, minimalist UI
- Glassmorphism is the dominant visual style
- Neumorphism is secondary and subtle
- No hard shadows or harsh contrast
- Strong visual hierarchy through color and font only

---

📄 **OUTPUT FORMAT (MANDATORY)**:
- Structure your response with clear section headers as shown above.
- Use bullet points and short, precise descriptions.
- Do NOT include font sizes, line height, CSS, layout, padding, spacing, or component dimensions.
- Do NOT include generic or placeholder values—be creative and specific.

---

**APPLICATION FLOW TO DESIGN**:
{flow}

**FINAL NOTE**:  
This output will be passed directly to a frontend agent. Keep it clean, precise, and only focused on visual decisions. Ensure the configuration is modern, visually appealing, and ready for direct implementation.
""",
    input_variables=["flow"],
)

llm = ChatGoogleGenerativeAI(model = "gemini-2.0-flash",temperature=0.1)


design_chain = design_prompt | llm