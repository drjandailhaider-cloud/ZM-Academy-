# ═══════════════════════════════════════════════════════════════════════════════
# ZM Academy — Complete Streamlit App
# FIXED VERSION: All bugs corrected
# ═══════════════════════════════════════════════════════════════════════════════
import streamlit as st
import json, hashlib, datetime, time, os, base64, random, io
from anthropic import Anthropic

# ══════════════════════════════════════════════════════════════
# TTS ENGINE — OpenAI neural voice (onyx), cached, toggleable
# ══════════════════════════════════════════════════════════════
def _clean_for_tts(text):
    """Strip markdown and normalise text for clean speech."""
    import re
    t = text
    for sym in ["**","*","###","##","#","```","__","_","---"]:
        t = t.replace(sym, "")
    # Remove URLs
    t = re.sub(r"http\S+", "", t)
    # Collapse whitespace
    t = " ".join(t.split())
    return t[:700]   # cap to keep latency low

def speak_text(text):
    """
    Generate MP3 via OpenAI TTS with gTTS fallback.
    • Skips if voice is OFF, text unchanged (cache hit), or both APIs unavailable.
    • On success: stores base64 MP3 in _tts_b64 + fingerprint in _tts_last_text.
    • On failure: sets _tts_b64 = None (text-only fallback, no crash).
    """
    # ── 1. Voice toggle gate ───────────────────────────────────────
    if not st.session_state.get("_voice_on", True):
        return

    clean = _clean_for_tts(text)
    if not clean:
        return

    # ── 2. Cache hit — exact same text already spoken ─────────────
    if st.session_state.get("_tts_last_text") == clean:
        return  # _tts_b64 already holds this audio

    # ── 3. Try OpenAI TTS (primary) ───────────────────────────────
    try:
        import openai
        oai_key = (st.secrets.get("OPENAI_API_KEY", "") or
                   os.environ.get("OPENAI_API_KEY", ""))
        if oai_key:
            c = openai.OpenAI(api_key=oai_key)
            r = c.audio.speech.create(
                model="tts-1",          # tts-1 = lowest latency
                voice="onyx",           # deep natural male teacher voice
                input=clean,
                response_format="mp3",
            )
            st.session_state["_tts_b64"]       = base64.b64encode(r.content).decode("ascii")
            st.session_state["_tts_last_text"] = clean
            return                      # success — done
    except Exception:
        pass  # fall through to gTTS

    # ── 4. gTTS fallback (free, no API key required) ──────────────
    try:
        from gtts import gTTS
        import io
        tts = gTTS(text=clean, lang="en", slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        st.session_state["_tts_b64"]       = base64.b64encode(buf.read()).decode("ascii")
        st.session_state["_tts_last_text"] = clean
    except Exception:
        st.session_state["_tts_b64"] = None   # total failure → text-only, no crash
# ─────────────────────────────────────────────────────────────────
# CAMBRIDGE + PAKISTAN NATIONAL CURRICULUM
# Grades 1–10, O Level, A Level
# Subjects: Maths, Physics, Chemistry, Biology, English, CS, Urdu
# ─────────────────────────────────────────────────────────────────
def _u(name, topics): return {"unit": name, "topics": topics}

CAMBRIDGE_CURRICULUM = {}

# ── MATHS ─────────────────────────────────────────────────────────
CAMBRIDGE_CURRICULUM["Maths"] = {
  "Grade 1": {"board":"Pakistan National Curriculum","units":[
    _u("Numbers 1–100",["Counting to 100","Number names","Before, after, between","Comparing numbers","Ordinal numbers 1st–10th"]),
    _u("Addition & Subtraction",["Adding single digits","Subtracting single digits","Number bonds to 10","Word problems"]),
    _u("Shapes & Measurement",["2D shapes: circle, square, triangle, rectangle","3D shapes: cube, sphere, cylinder","Long and short","Heavy and light","Measuring with non-standard units"]),
    _u("Patterns & Data",["Repeating patterns","Sorting objects","Simple pictographs","More and fewer"]),
  ]},
  "Grade 2": {"board":"Pakistan National Curriculum","units":[
    _u("Numbers to 1000",["Place value: hundreds, tens, ones","Reading and writing numbers","Comparing and ordering","Even and odd numbers","Skip counting 2s, 5s, 10s"]),
    _u("Addition & Subtraction",["Adding 2-digit numbers with regrouping","Subtracting with borrowing","Mental strategies","Word problems"]),
    _u("Multiplication & Division",["Multiplication as repeated addition","Times tables 2, 5, 10","Division as sharing equally","Simple division facts"]),
    _u("Fractions",["Half, quarter, third","Equal parts of shapes","Fractions of a set","Comparing simple fractions"]),
    _u("Geometry & Measurement",["Lines: straight and curved","Right angles","Perimeter of simple shapes","Telling time to half hour","Calendar and months"]),
  ]},
  "Grade 3": {"board":"Pakistan National Curriculum","units":[
    _u("Numbers & Place Value",["Numbers to 10,000","Place value to thousands","Rounding to nearest 10 and 100","Roman numerals I–XII","Negative numbers introduction"]),
    _u("Operations",["Addition with regrouping (4 digits)","Subtraction with regrouping","Multiplication tables 2–10","Long multiplication 2×1 digit","Division with remainders"]),
    _u("Fractions & Decimals",["Equivalent fractions","Comparing fractions","Tenths as decimals","Adding fractions with same denominator"]),
    _u("Geometry",["Angles: right, acute, obtuse","Perimeter of polygons","Area by counting squares","Parallel and perpendicular lines","Symmetry"]),
    _u("Data Handling",["Tally charts","Bar charts","Pictograms","Collecting and recording data"]),
  ]},
  "Grade 4": {"board":"Pakistan National Curriculum","units":[
    _u("Numbers",["Numbers to 1,000,000","Prime and composite numbers","Factors and multiples","LCM and HCF","Negative numbers on number line"]),
    _u("Fractions & Decimals",["Mixed numbers and improper fractions","Adding/subtracting unlike fractions","Multiplying fractions","Decimals to hundredths","Rounding decimals"]),
    _u("Algebra Basics",["Number patterns and rules","Simple equations: x+3=7","Variables and expressions","Function machines"]),
    _u("Measurement",["Area of triangles","Volume of cuboids","Units of length, mass, capacity","Converting between units","Perimeter of compound shapes"]),
    _u("Geometry",["Properties of quadrilaterals","Angles in triangles sum to 180°","Coordinates in first quadrant","Translation and reflection"]),
  ]},
  "Grade 5": {"board":"Pakistan National Curriculum","units":[
    _u("Number Theory",["Prime factorisation","LCM and HCF using prime factors","Indices/powers and square roots","BODMAS/BIDMAS","Estimation and approximation"]),
    _u("Fractions, Decimals & Percentages",["Converting fractions, decimals, percentages","Percentage of a quantity","Profit and loss","Discount","Ratio and proportion"]),
    _u("Algebra",["Algebraic expressions and simplification","Solving simple linear equations","Substitution into formulae","Sequences and patterns"]),
    _u("Geometry & Mensuration",["Area of circles: πr²","Volume of prisms","Surface area","Coordinates in all four quadrants","Interior and exterior angles"]),
    _u("Data & Statistics",["Pie charts","Bar graphs and line graphs","Mean, median, mode, range","Basic probability"]),
  ]},
  "Grade 6": {"board":"Cambridge Lower Secondary (0862)","units":[
    _u("Number",["Integers and ordering","Factors, multiples, primes, LCM, HCF","Powers and roots","Fractions, decimals, percentages","Ratio and proportion","Standard form introduction"]),
    _u("Algebra",["Algebraic notation","Simplifying expressions","Expanding brackets","Solving linear equations","Substitution","Sequences and term-to-term rules","Coordinates and graphs"]),
    _u("Geometry",["Angles on lines and at points","Properties of triangles and quadrilaterals","Circles: radius, diameter, circumference","Transformations: reflection, rotation, translation","Construction with compass and ruler"]),
    _u("Statistics & Probability",["Mean, median, mode, range","Bar charts, pie charts, line graphs","Frequency tables","Probability scale 0 to 1","Listing outcomes"]),
  ]},
  "Grade 7": {"board":"Cambridge Lower Secondary (0862)","units":[
    _u("Number",["Ordering integers and decimals","Percentage increase and decrease","Reverse percentages","Standard form","Rational and irrational numbers"]),
    _u("Algebra",["Expanding and factorising expressions","Equations with unknowns on both sides","Linear inequalities","Straight-line graphs: y = mx + c","Gradient and y-intercept","Simultaneous equations introduction"]),
    _u("Geometry",["Area of compound shapes","Surface area of prisms and cylinders","Volume of cylinders: πr²h","Bearings","Congruence and similarity","Pythagoras' theorem"]),
    _u("Statistics & Probability",["Scatter graphs and correlation","Two-way tables","Combined events and sample space","Relative frequency","Comparing distributions"]),
  ]},
  "Grade 8": {"board":"Cambridge Lower Secondary (0862)","units":[
    _u("Number",["Laws of indices","Introduction to surds","Upper and lower bounds","Direct and inverse proportion","Problems involving percentage"]),
    _u("Algebra",["Quadratic expressions: expanding (a+b)²","Factorising quadratics","Solving quadratics by factorisation","Simultaneous equations: elimination and substitution","Graphing quadratics"]),
    _u("Geometry",["Trigonometry: sin, cos, tan","Circle theorems","Vectors: addition and scalar multiplication","Loci and constructions","3D shapes and Pythagoras"]),
    _u("Statistics",["Cumulative frequency graphs","Box-and-whisker plots","Histograms","Stratified sampling","Comparing distributions"]),
  ]},
  "Grade 9": {"board":"Cambridge IGCSE Mathematics (0580)","units":[
    _u("Number",["Types of numbers","Indices and standard form","Ratio, rate and proportion","Compound interest and reverse percentages","Surds"]),
    _u("Algebra",["Algebraic manipulation","Linear and quadratic equations","Simultaneous equations","Inequalities","Functions: domain and range","Arithmetic and geometric sequences"]),
    _u("Coordinate Geometry",["Gradient and equation of a line","Parallel and perpendicular lines","Distance and midpoint formulae","Graphs of functions","Distance–time and speed–time graphs"]),
    _u("Geometry & Trigonometry",["Circle theorems","Pythagoras and trigonometry","Sine and cosine rules","Arc length and sector area","Vectors","Transformations"]),
    _u("Statistics & Probability",["Sampling and data collection","Averages and spread","Histograms and cumulative frequency","Tree diagrams","Conditional probability"]),
  ]},
  "Grade 10": {"board":"Cambridge IGCSE Mathematics (0580) Extended","units":[
    _u("Advanced Algebra",["Quadratic formula and completing the square","Algebraic fractions","Remainder and factor theorems","Binomial expansion","Partial fractions"]),
    _u("Functions & Graphs",["Domain and range","Composite and inverse functions","Exponential and logarithmic functions","Differentiation introduction","Rates of change"]),
    _u("Advanced Trigonometry",["Sine and cosine rules","Trigonometric graphs","Solving trig equations","3D trigonometry","Radians"]),
    _u("Matrices & Transformations",["Matrix operations","Determinant and inverse","Transformation matrices","Combined transformations"]),
    _u("Statistics",["Standard deviation","Conditional probability","Normal distribution introduction","Regression lines"]),
  ]},
  "O Level": {"board":"Cambridge O Level Mathematics (4024)","units":[
    _u("Number & Algebra",["Number systems","Algebraic expressions","Equations and inequalities","Matrices","Vectors","Functions"]),
    _u("Geometry & Trigonometry",["Circle theorems","Trigonometry in 2D and 3D","Mensuration","Transformations","Loci"]),
    _u("Statistics & Probability",["Statistical diagrams","Averages and spread","Probability","Cumulative frequency"]),
  ]},
  "A Level": {"board":"Cambridge A Level Mathematics (9709)","units":[
    _u("Pure 1",["Quadratics","Functions","Coordinate geometry","Binomial expansion","Trigonometry","Vectors","Differentiation","Integration"]),
    _u("Pure 2 & 3",["Algebra","Logarithms and exponentials","Trigonometry","Differential equations","Complex numbers","Numerical methods"]),
    _u("Statistics 1",["Data representation","Permutations and combinations","Probability","Discrete random variables","Normal distribution"]),
    _u("Mechanics 1",["Forces and equilibrium","Kinematics in 1D","Newton's laws","Energy, work and power","Momentum"]),
  ]},
}

# ── PHYSICS ───────────────────────────────────────────────────────
CAMBRIDGE_CURRICULUM["Physics"] = {
  "Grade 1": {"board":"Pakistan National Curriculum (Science)","units":[
    _u("Forces & Motion",["Push and pull forces","Moving and stationary objects","Fast and slow","Friction basics"]),
    _u("Light & Sound",["Sources of light","Light travels in straight lines","Loud and soft sounds","High and low pitch"]),
    _u("Materials",["Hard and soft","Rough and smooth","Waterproof materials","Magnetic and non-magnetic"]),
  ]},
  "Grade 2": {"board":"Pakistan National Curriculum (Science)","units":[
    _u("Forces",["Gravity pulls things down","Floating and sinking","Stretching and squashing"]),
    _u("Light",["Transparent and opaque materials","Shadows","Day and night"]),
    _u("Sound",["Sound made by vibrations","Travelling through materials","Volume and pitch"]),
  ]},
  "Grade 3": {"board":"Pakistan National Curriculum (Science)","units":[
    _u("Forces & Magnets",["Types of forces","Magnetic force","Poles of a magnet","Friction and its effects","Balanced and unbalanced forces"]),
    _u("Light",["Light sources","Reflection","Shadows and their properties","Colour spectrum"]),
    _u("Sound",["How sound travels","Loudness and pitch","Musical instruments","Sound absorption"]),
  ]},
  "Grade 4": {"board":"Pakistan National Curriculum (Science)","units":[
    _u("Electricity",["Simple circuits","Conductors and insulators","Series and parallel circuits","Switches","Electrical safety"]),
    _u("Energy",["Forms of energy","Energy transfers","Renewable sources","Non-renewable sources","Saving energy"]),
    _u("Forces & Motion",["Speed and distance","Measuring speed","Gravity","Air resistance"]),
  ]},
  "Grade 5": {"board":"Pakistan National Curriculum (Science)","units":[
    _u("Forces & Space",["Gravity and weight","Mass vs weight","The solar system","Earth's orbit and seasons"]),
    _u("Electricity & Magnetism",["Current and voltage","Circuit diagrams","Electromagnets","Magnetic fields"]),
    _u("Earth Sciences",["Rock cycle","Weathering and erosion","Water cycle","Natural disasters"]),
  ]},
  "Grade 6": {"board":"Cambridge Lower Secondary (0893)","units":[
    _u("Forces & Motion",["Contact and non-contact forces","Balanced and unbalanced forces","Friction and air resistance","Gravity and weight","Speed = distance ÷ time"]),
    _u("Energy",["Forms of energy","Energy transfers and transformations","Renewable energy","Non-renewable energy","Conservation of energy"]),
    _u("Sound & Light",["Sound wave properties: amplitude, frequency","Reflection and echo","Reflection of light","Refraction introduction","Colour spectrum"]),
  ]},
  "Grade 7": {"board":"Cambridge Lower Secondary (0893)","units":[
    _u("Matter & Properties",["States of matter and particle model","Density: mass ÷ volume","Pressure in fluids","Upthrust and Archimedes' principle","Gas pressure"]),
    _u("Electricity & Magnetism",["Static electricity","Series and parallel circuits","Resistance and Ohm's law introduction","Magnetic fields","Electromagnets and applications"]),
    _u("Waves",["Wave properties: amplitude, frequency, wavelength","Transverse and longitudinal waves","Electromagnetic spectrum","Uses of EM waves","Sound and hearing"]),
  ]},
  "Grade 8": {"board":"Cambridge Lower Secondary (0893)","units":[
    _u("Mechanics",["Speed, velocity and acceleration","Distance-time graphs","Velocity-time graphs","Newton's three laws","Momentum and impulse"]),
    _u("Thermal Physics",["Specific heat capacity","Latent heat: melting and boiling","Conduction, convection and radiation","Thermal expansion","Gas laws: Boyle's and Charles's"]),
    _u("Space Physics",["The solar system","Stellar life cycles","Galaxies and universe","Gravitational fields and orbits","Satellites"]),
  ]},
  "Grade 9": {"board":"Cambridge IGCSE Physics (0625)","units":[
    _u("General Physics",["Measurements and SI units","Scalars and vectors","Velocity and acceleration","Forces and Newton's laws","Moments and equilibrium","Work, energy, power","Pressure"]),
    _u("Thermal Physics",["Kinetic theory","Thermometers and temperature scales","Specific heat capacity","Specific latent heat","Gas laws and Kelvin scale","Heat transfer"]),
    _u("Waves",["General wave properties","Sound waves","Reflection and refraction of light","Total internal reflection","Lenses","Electromagnetic spectrum"]),
    _u("Electricity & Magnetism",["Electric charge and current","Potential difference and resistance","Ohm's law","Series and parallel circuits","Electromagnetic induction","Transformers"]),
    _u("Atomic Physics",["Atomic structure","Radioactive emissions: α, β, γ","Nuclear equations","Half-life","Uses and dangers of radiation","Nuclear fission and fusion"]),
  ]},
  "Grade 10": {"board":"Cambridge IGCSE Physics (0625) Extended","units":[
    _u("Advanced Mechanics",["Projectile motion","Circular motion and centripetal force","Gravitational fields","Satellite orbital speed"]),
    _u("Advanced Electricity",["Internal resistance and EMF","Kirchhoff's laws","Capacitors","Semiconductors and diodes","Logic gates"]),
    _u("Waves & Optics",["Interference and diffraction","Young's double-slit experiment","Polarisation","Doppler effect","Optical fibres"]),
    _u("Nuclear Physics",["Mass-energy equivalence: E = mc²","Nuclear fission reactors","Nuclear fusion","Binding energy per nucleon"]),
  ]},
  "O Level": {"board":"Cambridge O Level Physics (5054)","units":[
    _u("Mechanics",["Measurements","Kinematics","Dynamics and Newton's laws","Mass, weight, density","Moments","Energy and power","Pressure"]),
    _u("Thermal Physics",["Kinetic theory","Thermal properties","Heat transfer: conduction, convection, radiation"]),
    _u("Waves",["General waves","Light and optics","Electromagnetic spectrum","Sound"]),
    _u("Electricity & Magnetism",["Magnetism","Electrical quantities","Circuits","Practical electricity","Electromagnetic effects"]),
    _u("Atomic Physics",["Radioactivity","Nuclear energy"]),
  ]},
  "A Level": {"board":"Cambridge A Level Physics (9702)","units":[
    _u("Measurement & Mechanics",["SI units, scalars and vectors","Kinematics equations","Newton's laws and momentum","Circular motion","Gravitational fields","Oscillations and SHM"]),
    _u("Matter & Thermal Physics",["Deformation of solids: Hooke's law","Thermal properties of materials","Ideal gases and kinetic theory"]),
    _u("Waves & Superposition",["Progressive waves","Superposition and interference","Diffraction","EM waves and polarisation"]),
    _u("Electricity & Electromagnetism",["Electric fields and potential","Capacitance","Magnetic fields","Electromagnetic induction","AC theory and transformers"]),
    _u("Modern & Quantum Physics",["Photoelectric effect","de Broglie wavelength","Atomic spectra","Nuclear physics","Medical imaging","Astrophysics"]),
  ]},
}

# ── CHEMISTRY ─────────────────────────────────────────────────────
CAMBRIDGE_CURRICULUM["Chemistry"] = {
  "Grade 1": {"board":"Pakistan National Curriculum (Science)","units":[
    _u("Materials",["Names of common materials","Properties: hard/soft, rough/smooth","Natural and man-made materials","Uses of materials"]),
  ]},
  "Grade 2": {"board":"Pakistan National Curriculum (Science)","units":[
    _u("Materials & Changes",["Solid, liquid, gas","Melting and freezing","Water and ice","Mixing materials"]),
  ]},
  "Grade 3": {"board":"Pakistan National Curriculum (Science)","units":[
    _u("Rocks & Soils",["Types of rocks","Properties of rocks","Soil types","Fossils"]),
    _u("States of Matter",["Particle theory introduction","Evaporation and condensation","Dissolving and solutions","Filtering"]),
  ]},
  "Grade 4": {"board":"Pakistan National Curriculum (Science)","units":[
    _u("Materials & Properties",["Thermal and electrical conductors","Insulators","Magnetic materials","Reversible and irreversible changes"]),
    _u("Mixtures & Separation",["Mixtures and solutions","Filtering and evaporation","Distillation introduction","Solubility"]),
  ]},
  "Grade 5": {"board":"Pakistan National Curriculum (Science)","units":[
    _u("Chemical Changes",["Physical vs chemical change","Burning","Rusting","Signs of chemical reactions","Acids and bases: pH scale"]),
    _u("Earth & Resources",["Earth's structure","Rock cycle","Water cycle","Fossil fuels","Renewable resources"]),
  ]},
  "Grade 6": {"board":"Cambridge Lower Secondary (0893)","units":[
    _u("States of Matter",["Solids, liquids and gases","Particle model and kinetic theory","Changes of state","Evaporation and condensation","Diffusion"]),
    _u("Elements, Compounds & Mixtures",["Elements and the periodic table","Compounds vs mixtures","Chemical formulae","Acids and alkalis","pH scale and indicators"]),
    _u("Separating Mixtures",["Filtration","Evaporation to dryness","Simple distillation","Chromatography","Crystallisation"]),
  ]},
  "Grade 7": {"board":"Cambridge Lower Secondary (0893)","units":[
    _u("Atoms & Elements",["Atomic structure: protons, neutrons, electrons","Proton number and mass number","Isotopes","Periodic table: groups and periods","Symbols and formulae"]),
    _u("Chemical Reactions",["Physical and chemical changes","Word equations","Conservation of mass","Exothermic and endothermic reactions","Burning reactions"]),
    _u("Metals & Non-Metals",["Properties of metals","Properties of non-metals","Reactions of metals with oxygen, water, acid","Metal oxides","Displacement reactions"]),
  ]},
  "Grade 8": {"board":"Cambridge Lower Secondary (0893)","units":[
    _u("Periodic Table",["Groups I, II, VII, 0","Alkali metals","Halogens","Noble gases","Transition metals","Trends across periods"]),
    _u("Chemical Bonding",["Ionic bonding: electron transfer","Covalent bonding: electron sharing","Metallic bonding","Properties related to bonding","Giant structures"]),
    _u("Acids, Bases & Salts",["Properties of acids and bases","Neutralisation","Making salts","Precipitation reactions","Ionic equations"]),
  ]},
  "Grade 9": {"board":"Cambridge IGCSE Chemistry (0620)","units":[
    _u("Principles of Chemistry",["Atomic structure and subatomic particles","The Periodic Table: trends and groups","Ionic, covalent and metallic bonding","Chemical formulae and equations","Stoichiometry and mole concept","Electrolysis"]),
    _u("Physical Chemistry",["Energetics: exothermic and endothermic","Rates of reaction: factors","Reversible reactions and equilibrium","Oxidation and reduction (redox)","Electrochemical cells"]),
    _u("Inorganic Chemistry",["Reactivity series of metals","Extraction of metals: iron, aluminium","Corrosion and prevention","Acids, bases, salts","Ammonia and the Haber process","Sulfuric acid and its uses"]),
    _u("Organic Chemistry",["Introduction to organic chemistry","Alkanes: properties and reactions","Alkenes: addition reactions","Ethanol: fermentation and hydration","Carboxylic acids","Addition and condensation polymers"]),
  ]},
  "Grade 10": {"board":"Cambridge IGCSE Chemistry (0620) Extended","units":[
    _u("Advanced Stoichiometry",["Mole calculations","Empirical and molecular formulae","Titration calculations","Gas volume calculations","Yield and percentage purity"]),
    _u("Advanced Organic Chemistry",["Structural and geometric isomerism","Benzene and aromatic compounds","Condensation polymerisation: nylon, polyesters","Amino acids and proteins","Carbohydrates and fats"]),
    _u("Advanced Physical Chemistry",["Enthalpy cycle: Hess's law","Activation energy and catalysts","Le Chatelier's principle","Quantitative electrolysis (Faraday)","Electrochemical series"]),
    _u("Analytical Chemistry",["Identifying ions: flame tests and precipitates","Gas tests: CO₂, H₂, O₂, NH₃, Cl₂","Chromatography Rf values","Identifying organic compounds","Instrumental analysis introduction"]),
  ]},
  "O Level": {"board":"Cambridge O Level Chemistry (5070)","units":[
    _u("Physical & Inorganic Chemistry",["Atomic structure","Bonding","Stoichiometry","Electrolysis","Energetics","Kinetics","Equilibrium","Acids, bases and salts","Periodic table","Metals","Nitrogen and sulfur"]),
    _u("Organic Chemistry",["Alkanes","Alkenes","Alcohols","Halogenoalkanes","Carboxylic acids","Esters","Amines","Amino acids","Polymers","Benzene"]),
  ]},
  "A Level": {"board":"Cambridge A Level Chemistry (9701)","units":[
    _u("Physical Chemistry",["Atoms, molecules and stoichiometry","Atomic structure","Chemical bonding and structure","States of matter","Chemical energetics","Electrochemistry","Equilibria","Reaction kinetics"]),
    _u("Inorganic Chemistry",["Periodicity","Group 2 and Group 17","Period 3","Transition elements","Nitrogen and sulfur chemistry"]),
    _u("Organic Chemistry",["Hydrocarbons","Halogen compounds","Hydroxy compounds","Carbonyl compounds","Carboxylic acids and derivatives","Nitrogen compounds","Polymerisation","Spectroscopic techniques"]),
  ]},
}

# ── BIOLOGY ───────────────────────────────────────────────────────
CAMBRIDGE_CURRICULUM["Biology"] = {
  "Grade 1": {"board":"Pakistan National Curriculum (Science)","units":[
    _u("Living Things",["Animals and plants","Habitats","Basic food chains","Life cycles","Caring for living things"]),
    _u("Human Body",["Main body parts","Five senses","Healthy foods","Exercise and hygiene","Growing and changing"]),
  ]},
  "Grade 2": {"board":"Pakistan National Curriculum (Science)","units":[
    _u("Plants",["Parts of a plant: roots, stem, leaves, flower","What plants need to grow","Seeds and germination","Photosynthesis basics"]),
    _u("Animals",["Animal groups: mammals, birds, fish, reptiles, amphibians","Food chains","Habitats and adaptation","Life cycles"]),
    _u("Human Body",["Skeletal system","Muscular system","Digestive system basics","Healthy diet and exercise"]),
  ]},
  "Grade 3": {"board":"Pakistan National Curriculum (Science)","units":[
    _u("Life Processes",["MRS GREN overview","Photosynthesis","Respiration basics","Nutrition in animals","Excretion"]),
    _u("Ecosystems",["Food webs","Producers and consumers","Decomposers","Habitats: forest, desert, ocean","Adaptation"]),
    _u("Human Health",["Diseases: bacteria and viruses","Hygiene and prevention","Vaccines and immunity","Medicines"]),
  ]},
  "Grade 4": {"board":"Pakistan National Curriculum (Science)","units":[
    _u("Cells",["Plant and animal cells","Cell parts: nucleus, cytoplasm, membrane, wall","Unicellular organisms","Using a microscope"]),
    _u("Reproduction",["Plant reproduction: pollination, fertilisation, seed dispersal","Animal reproduction","Human life cycle"]),
    _u("Environment",["Carbon cycle","Nitrogen cycle","Pollution types","Conservation","Endangered species"]),
  ]},
  "Grade 5": {"board":"Pakistan National Curriculum (Science)","units":[
    _u("Body Systems",["Circulatory system: heart and blood","Respiratory system","Nervous system basics","Digestive system in detail","Excretory system"]),
    _u("Genetics & Variation",["Heredity basics","Variation in species","Natural selection introduction","Selective breeding"]),
    _u("Ecology",["Biomes of the world","Energy flow in ecosystems","Human impact","Sustainable development"]),
  ]},
  "Grade 6": {"board":"Cambridge Lower Secondary (0893)","units":[
    _u("Cells & Organisation",["Plant and animal cells: structure and function","Cell organelles","Unicellular vs multicellular","Tissues, organs, organ systems","Using a light microscope"]),
    _u("Ecosystems",["Biotic and abiotic factors","Food chains and webs","Producers, consumers, decomposers","Adaptation to environments","Competition and predation"]),
    _u("Human Body Systems",["Skeletal and muscular systems","Digestive system: digestion and absorption","Circulatory system overview","Teeth types and functions","Healthy lifestyle"]),
  ]},
  "Grade 7": {"board":"Cambridge Lower Secondary (0893)","units":[
    _u("Life Processes",["MRS GREN in detail","Photosynthesis: equation and factors","Aerobic and anaerobic respiration","Nutrition: balanced diet and food tests","Excretion in humans and plants"]),
    _u("Reproduction",["Sexual and asexual reproduction","Flowering plant reproduction","Human reproductive system","Menstrual cycle","Pregnancy and development"]),
    _u("Environment & Ecology",["Carbon and nitrogen cycles","Decomposers and decay","Pollution: air, water, land","Conservation strategies","Climate change and biodiversity"]),
  ]},
  "Grade 8": {"board":"Cambridge Lower Secondary (0893)","units":[
    _u("Cells & Biological Molecules",["Prokaryotic vs eukaryotic cells","Osmosis and diffusion","Active transport","Carbohydrates, lipids, proteins","Enzymes: activity, denaturation, pH"]),
    _u("Disease & Immunity",["Pathogens: bacteria, viruses, fungi, parasites","How diseases spread","Immune system: antibodies and phagocytes","Vaccination","Antibiotics and limitations"]),
    _u("Genetics & Variation",["DNA structure: double helix and bases","Chromosomes and genes","Mitosis: growth and repair","Meiosis: sexual reproduction","Inheritance: dominant and recessive","Mutations and genetic disorders"]),
  ]},
  "Grade 9": {"board":"Cambridge IGCSE Biology (0610)","units":[
    _u("Characteristics & Classification",["Characteristics of living organisms","Classification: kingdom to species","Dichotomous keys","Cell structure: animal, plant, bacterial","Biological molecules and enzymes"]),
    _u("Nutrition",["Photosynthesis: equation and limiting factors","Human digestive system","Enzymes in digestion","Absorption in small intestine","Malnutrition and deficiency diseases"]),
    _u("Respiration & Gas Exchange",["Aerobic respiration equation","Anaerobic respiration in muscles and yeast","Gas exchange in humans: alveoli","Gas exchange in plants: stomata","Breathing mechanism"]),
    _u("Transport",["Blood: plasma, red cells, white cells, platelets","Blood vessels: artery, vein, capillary","Heart structure and cardiac cycle","Double circulatory system","Transport in plants: xylem and phloem","Transpiration and factors"]),
    _u("Excretion & Coordination",["Kidney structure and ultrafiltration","Nervous system: neurones and reflex arc","Hormones: insulin, glucagon, ADH","Homeostasis: temperature and blood glucose","Eye and ear structure"]),
    _u("Reproduction & Genetics",["Human reproduction: fertilisation to birth","Cell division: mitosis and meiosis","Monohybrid inheritance","Codominance","Natural selection and evolution"]),
  ]},
  "Grade 10": {"board":"Cambridge IGCSE Biology (0610) Extended","units":[
    _u("Advanced Genetics",["Dihybrid crosses","Codominance and multiple alleles","Sex-linked inheritance: haemophilia, colour blindness","Genetic engineering: insulin production","Selective breeding","Cloning: tissue culture"]),
    _u("Advanced Physiology",["Kidney failure: dialysis and transplant","Plant hormones: auxins and phototropism","Immune response: T and B lymphocytes","Biotechnology: fermenters","Brain regions and functions"]),
    _u("Ecology & Environment",["Energy flow and trophic levels","Carbon and nitrogen cycles in detail","Human population growth impact","Deforestation and habitat destruction","Conservation strategies","Global warming and climate change"]),
  ]},
  "O Level": {"board":"Cambridge O Level Biology (5090)","units":[
    _u("Cell Biology",["Cell structure","Biological molecules","Enzymes","Cell division","Transport in cells"]),
    _u("Physiology",["Nutrition","Transport","Respiration","Gas exchange","Excretion","Coordination","Reproduction","Growth"]),
    _u("Genetics, Evolution & Ecology",["Inheritance and variation","Natural selection","Ecosystems","Human impact on environment"]),
  ]},
  "A Level": {"board":"Cambridge A Level Biology (9700)","units":[
    _u("Cell Biology & Biochemistry",["Cell ultrastructure","Biological molecules","Enzyme kinetics","Membrane structure and transport","Cell division"]),
    _u("Physiology",["Gas exchange in plants, insects, fish","Transport in plants","Transport in mammals","Nutrition and digestion","Excretion","Homeostasis","Nervous coordination","Hormonal coordination","Reproduction"]),
    _u("Genetics & Evolution",["Inheritance: mono, di, sex-linked","Population genetics","Selection and speciation","Mutations and cancer"]),
    _u("Ecology",["Energy and nutrient cycles","Populations and communities","Human impact and conservation"]),
    _u("Biochemistry",["Photosynthesis: light-dependent and light-independent","Respiration: glycolysis, Krebs cycle, oxidative phosphorylation","Genetic technology"]),
  ]},
}

# ── ENGLISH ───────────────────────────────────────────────────────
CAMBRIDGE_CURRICULUM["English"] = {
  "Grade 1": {"board":"Pakistan National Curriculum","units":[
    _u("Phonics & Reading",["Alphabet sounds (phonics)","CVC words: cat, dog, pen","Sight words","Simple sentences","Reading aloud"]),
    _u("Writing",["Letter formation","Copying words and sentences","Capital letters and full stops","Writing own name"]),
    _u("Listening & Speaking",["Listening to and retelling stories","Answering simple questions","Describing pictures","Basic conversation"]),
  ]},
  "Grade 2": {"board":"Pakistan National Curriculum","units":[
    _u("Reading & Comprehension",["Reading short texts","Answering literal questions","Identifying characters and setting","Sequencing story events","Word meanings in context"]),
    _u("Grammar",["Nouns: common and proper","Pronouns","Verbs","Adjectives","Plural nouns","Simple present and past tense"]),
    _u("Writing",["Writing sentences","Punctuation: full stop, question mark, exclamation mark","Simple paragraphs","Short stories"]),
  ]},
  "Grade 3": {"board":"Pakistan National Curriculum","units":[
    _u("Reading",["Comprehension strategies","Main idea and supporting details","Making inferences","Skimming and scanning","Different text types"]),
    _u("Grammar",["Parts of speech","Simple and continuous tenses","Articles: a, an, the","Prepositions","Conjunctions","Comma and apostrophe"]),
    _u("Writing",["Paragraph structure","Narrative writing","Descriptive writing","Informal letters","Dictionary and thesaurus use"]),
  ]},
  "Grade 4": {"board":"Pakistan National Curriculum","units":[
    _u("Reading",["Fact and opinion","Summarising a text","Author's purpose","Figurative language: simile, metaphor","Poetry: rhyme, rhythm"]),
    _u("Grammar",["Main and subordinate clauses","Active and passive voice","Direct and indirect speech","Conditional sentences","Modal verbs"]),
    _u("Writing",["Five-paragraph essay","Persuasive writing","Report writing","Story writing: plot structure","Editing and proofreading"]),
  ]},
  "Grade 5": {"board":"Pakistan National Curriculum","units":[
    _u("Reading",["Analysing texts","Comparing two texts","Themes and messages","Literary devices: irony, symbolism","Non-fiction texts"]),
    _u("Grammar & Vocabulary",["Complex sentences","Relative clauses","Reported speech","Synonyms, antonyms, homonyms","Word roots, prefixes, suffixes"]),
    _u("Writing",["Formal and informal register","Argumentative essays","Creative writing techniques","Research note-taking","Presentation skills"]),
  ]},
  "Grade 6": {"board":"Cambridge Lower Secondary (0851)","units":[
    _u("Reading",["Fiction and non-fiction","Comprehension strategies","Inference and deduction","Author's viewpoint and purpose","Comparing texts"]),
    _u("Writing",["Narrative writing: structure and technique","Descriptive writing: sensory language","Formal letters","Reports and summaries","Planning and drafting"]),
    _u("Grammar & Vocabulary",["Tenses review","Sentence types","Punctuation: semicolon, colon, dash","Figurative language","Word formation: affixes"]),
    _u("Speaking & Listening",["Formal presentations","Group discussion and debate","Active listening and note-taking","Interviews","Role play"]),
  ]},
  "Grade 7": {"board":"Cambridge Lower Secondary (0851)","units":[
    _u("Reading",["Analysing language choices","Dramatic techniques in texts","Unseen poetry: form, structure, language","Media texts: bias and persuasion","Comparing texts from different periods"]),
    _u("Writing",["Discursive writing: balanced argument","Reviews: film, book, music","Newspaper and magazine articles","Creative writing: character and setting","Editing for impact"]),
    _u("Grammar",["Complex sentences with subordinate clauses","Passive voice for effect","All types of conditional sentences","Cohesive devices"]),
  ]},
  "Grade 8": {"board":"Cambridge Lower Secondary (0851)","units":[
    _u("Literature",["Short story analysis: narrative voice and structure","Poetry comparison: form, imagery, tone","Drama: stage directions and dialogue","Novel study: themes and character","Motifs and symbolism"]),
    _u("Language Skills",["Argumentative essays","Analytical writing with quotations","Language features and their effects","Tone, register and audience","Advanced proofreading"]),
    _u("Grammar",["Subjunctive mood","Participle clauses","Inversion for emphasis","Parenthetical phrases","Sentence rhythm and variety"]),
  ]},
  "Grade 9": {"board":"Cambridge IGCSE First Language English (0500)","units":[
    _u("Reading",["Comprehension: explicit and implicit","Inference questions: evidence-based","Summary writing: selecting key points","Comparison of two texts","Analysis of language, structure and effect"]),
    _u("Writing",["Descriptive writing: vivid language","Narrative writing: effective techniques","Persuasive writing: rhetorical devices","Argumentative writing: thesis and counterargument","Writing for audience and purpose"]),
    _u("Directed Writing",["Transforming text form: letter, speech, article","Writing from given information","Formal register and conventions","Combining source material","Directed writing accuracy"]),
  ]},
  "Grade 10": {"board":"Cambridge IGCSE First Language English (0500)","units":[
    _u("Extended Reading",["Analysing complex layered texts","Evaluating writer's craft","Comparing texts for purpose and effect","Unseen poetry: detailed analysis","Literary criticism introduction"]),
    _u("Extended Writing",["Distinction-level persuasive essays","Narrative technique: non-linear structure","Descriptive complexity: extended metaphor","Original composition and commentary","Editing for sophistication"]),
  ]},
  "O Level": {"board":"Cambridge O Level English Language (1123)","units":[
    _u("Reading",["Comprehension and summary","Directed writing from text","Implicit and explicit meaning","Language analysis","Evaluation of texts"]),
    _u("Writing",["Personal, descriptive and narrative","Argumentative and discursive","Formal and informal registers","Style and accuracy"]),
  ]},
  "A Level": {"board":"Cambridge A Level English Language (9093)","units":[
    _u("Language Analysis",["Spoken and written language features","Language variation: regional and social","Language change over time","Language and identity","Discourse analysis"]),
    _u("Writing & Editing",["Original writing for specific purpose","Coursework commentary","Analytical essays on language","Language frameworks","Critical analysis of unseen texts"]),
  ]},
}

# ── COMPUTER SCIENCE ──────────────────────────────────────────────
CAMBRIDGE_CURRICULUM["Computer Science"] = {
  "Grade 1": {"board":"Pakistan National Curriculum (ICT)","units":[
    _u("Introduction to Computers",["Parts of a computer: monitor, keyboard, mouse, CPU","Turning on and off safely","Using a mouse: click, double-click, drag","Basic typing","Computer care and safety"]),
  ]},
  "Grade 2": {"board":"Pakistan National Curriculum (ICT)","units":[
    _u("Basic Computer Skills",["Using keyboard and mouse","Opening and closing programs","Drawing with Paint","Saving files","Printing documents"]),
  ]},
  "Grade 3": {"board":"Pakistan National Curriculum (ICT)","units":[
    _u("Software & Internet",["Word processing: typing and formatting","Using the internet safely","Searching for information","Email basics","Passwords and digital safety"]),
    _u("Introduction to Programming",["What is a computer program?","Scratch: sprites and backgrounds","Events: when green flag clicked","Simple movement commands","Sequences in Scratch"]),
  ]},
  "Grade 4": {"board":"Pakistan National Curriculum (ICT)","units":[
    _u("Algorithms & Programming",["What is an algorithm?","Flowcharts: start, end, process, decision","Scratch: loops (repeat, forever)","Scratch: conditionals (if/else)","Debugging simple programs"]),
    _u("Digital Tools",["Spreadsheets: entering data and simple formulas","Presentations: slides and layout","Organising files and folders","Effective search engine use"]),
  ]},
  "Grade 5": {"board":"Pakistan National Curriculum (ICT)","units":[
    _u("Computer Systems",["Hardware vs software","Input and output devices","Storage devices: HDD, USB, cloud","Operating systems","Binary numbers introduction"]),
    _u("Programming",["Variables in Scratch","User input and output","Procedures in Scratch","Nested loops","Testing and debugging"]),
    _u("Internet & Society",["How the internet works","Networks: LAN and WAN","Cyberbullying","Copyright and fair use","Digital footprint"]),
  ]},
  "Grade 6": {"board":"Pakistan National Curriculum (ICT)","units":[
    _u("Computer Systems",["Hardware: CPU, RAM, ROM, storage","System and application software","Input devices","Output devices","Computer maintenance"]),
    _u("Programming (Python)",["Introduction: print and input","Variables and data types: int, str, float","Arithmetic operators","if/elif/else statements","for and while loops"]),
    _u("Networks & Safety",["LAN, WAN, internet","IP addresses and URLs","Email and communication tools","Online safety and privacy","Digital citizenship"]),
  ]},
  "Grade 7": {"board":"Pakistan National Curriculum (ICT)","units":[
    _u("Data Representation",["Binary number system","Converting binary to denary and back","Hexadecimal","ASCII character codes","Storage units: bit, byte, KB, MB, GB"]),
    _u("Programming (Python)",["Lists and tuples","String methods","Functions: defining and calling","Scope: local and global variables","Importing modules"]),
    _u("Networks & Security",["Network topologies: bus, star, ring","Network protocols: TCP/IP, HTTP","Cybersecurity threats: malware, phishing","Firewalls and antivirus","Encryption basics"]),
  ]},
  "Grade 8": {"board":"Pakistan National Curriculum (ICT)","units":[
    _u("Databases",["What is a database?","Tables, records and fields","Data types in databases","SQL: SELECT and WHERE","Sorting and filtering","Forms and reports"]),
    _u("Advanced Programming",["2D lists and dictionaries","File reading and writing","Exception handling: try/except","OOP: classes and objects","Pseudocode writing"]),
    _u("Systems Development",["Software development lifecycle (SDLC)","Requirements analysis","Testing: white-box and black-box","Evaluation and maintenance","Ethical issues in computing"]),
  ]},
  "Grade 9": {"board":"Cambridge IGCSE Computer Science (0478)","units":[
    _u("Data Representation",["Binary, denary, hexadecimal conversions","Binary arithmetic and overflow","Character encoding: ASCII and Unicode","Image representation: pixels, colour depth, resolution","Sound: sampling rate and bit depth","Lossless and lossy compression"]),
    _u("Computer Systems",["CPU: ALU, CU, MAR, MDR, PC, accumulator","Fetch-execute cycle","RAM and ROM","Secondary storage: HDD, SSD, optical, flash","Input and output devices"]),
    _u("Networks",["PAN, LAN, WAN, internet","Network hardware: hub, switch, router","Topologies: bus, star, mesh","Protocols: TCP/IP, HTTP, HTTPS, FTP, DNS","Wired vs wireless","Security threats and solutions"]),
    _u("Programming & Algorithms",["Sequence, selection, iteration","Data structures: arrays and records","Procedures and functions","Boolean logic and truth tables","Pseudocode and flowcharts","Sorting and searching algorithms"]),
    _u("Security, Ethics & Environment",["Malware, phishing, brute force attacks","Encryption, 2FA, access levels","Ethical and legal issues in computing","Environmental impact","Intellectual property and privacy"]),
  ]},
  "Grade 10": {"board":"Cambridge IGCSE Computer Science (0478)","units":[
    _u("Advanced Programming",["Python: full syntax revision","Bubble sort and merge sort implementation","Linear and binary search","Recursion","OOP: classes, inheritance, polymorphism"]),
    _u("Database & Web",["Relational databases: primary and foreign keys","SQL: SELECT, INSERT, UPDATE, DELETE, JOIN","HTML structure","CSS styling","JavaScript DOM basics","Web security: HTTPS, SQL injection"]),
    _u("Computational Thinking",["Decomposition","Abstraction","Pattern recognition","Algorithm efficiency: Big O introduction","System design and flowcharting"]),
  ]},
  "O Level": {"board":"Cambridge O Level Computer Science (2210)","units":[
    _u("Theory",["Data representation","Communication and internet technologies","Hardware","Software and development","Security and privacy","Ethics and sustainability"]),
    _u("Programming & Algorithms",["Algorithm design: pseudocode and flowcharts","Programming in Python","Data structures","Testing and debugging","Trace tables","Validation and verification"]),
    _u("Database & Spreadsheets",["Database design and SQL","Spreadsheet functions and formulas","Data manipulation","Charts and graphs"]),
  ]},
  "A Level": {"board":"Cambridge A Level Computer Science (9618)","units":[
    _u("Theory of CS",["Data representation","Communication","Hardware and virtual machines","Logic gates and Boolean algebra","Processor architecture","System software","Security and ethics"]),
    _u("Algorithms & Data Structures",["Algorithm design and analysis","Big O complexity","ADTs: stack, queue, linked list, tree, graph, hash table","Sorting algorithms","Graph traversal: BFS, DFS","Recursion"]),
    _u("Advanced Programming",["OOP: encapsulation, inheritance, polymorphism","File handling","Database: SQL and relational design","Web technologies","Functional programming","Declarative programming"]),
  ]},
}

# ── URDU ──────────────────────────────────────────────────────────
CAMBRIDGE_CURRICULUM["Urdu"] = {
  "Grade 1": {"board":"Pakistan National Curriculum","units":[
    _u("حروفِ تہجی",["حروف کی پہچان","حروف کی آوازیں","مصوتے: ا، و، ی","مصمتے","الف مد اور اس کا استعمال"]),
    _u("پڑھنا اور لکھنا",["حروف لکھنے کی مشق","آسان الفاظ پڑھنا","تصویروں کے نام","جوڑ توڑ: حروف ملانا"]),
  ]},
  "Grade 2": {"board":"Pakistan National Curriculum","units":[
    _u("قواعد",["اسم: جاندار اور بے جاندار","مذکر اور مؤنث","واحد اور جمع","فعل: کام کا لفظ","حرفِ جار"]),
    _u("پڑھنا اور لکھنا",["چھوٹی کہانیاں پڑھنا","مختصر جملے لکھنا","سوالوں کے جواب","الفاظ کے معنی"]),
  ]},
  "Grade 3": {"board":"Pakistan National Curriculum","units":[
    _u("قواعد",["اسم کی اقسام","ضمیر","صفت","فعل کی اقسام","زمانہ: حال، ماضی، مستقبل"]),
    _u("تحریر",["پیراگراف لکھنا","غیر رسمی خط","چھوٹی کہانی","الفاظ کے معنی و استعمال"]),
    _u("ادب",["آسان نظمیں","چھوٹی کہانیاں","محاورے","کہاوتیں"]),
  ]},
  "Grade 4": {"board":"Pakistan National Curriculum","units":[
    _u("ادب",["نظم و نثر میں فرق","مختصر کہانیاں","نظمیں یاد کرنا","محاورے اور ضرب الامثال","ادبی شخصیات"]),
    _u("قواعد",["مرکب جملے","فاعل اور مفعول","مصدر","حروفِ عطف","جملہ اسمیہ اور فعلیہ"]),
    _u("تحریر",["مضمون نویسی","رسمی خط","خلاصہ لکھنا","تصویر بیانی"]),
  ]},
  "Grade 5": {"board":"Pakistan National Curriculum","units":[
    _u("ادبی تفہیم",["علامہ اقبالؒ کی نظمیں","حمد و نعت","مختصر افسانے","ڈرامہ: مکالمہ","سفرنامہ"]),
    _u("قواعد و انشاء",["تراکیب: اضافی اور توصیفی","بیانِ واقعہ","متن کا تجزیہ","لغت کا استعمال"]),
  ]},
  "Grade 6": {"board":"Pakistan National Curriculum","units":[
    _u("نثر",["سبق کا خلاصہ","سوال و جواب","مرکزی خیال","کردار نگاری","اقتباس کی تشریح"]),
    _u("نظم",["نظم کی تشریح","شاعر کا تعارف","اصنافِ سخن: نظم، غزل، قطعہ","نعت","حمد"]),
    _u("قواعد",["اسم کی اقسام","فعل لازم اور متعدی","حروف","مرکب الفاظ","تذکیر و تانیث"]),
    _u("تحریر",["مضمون نویسی","کہانی نویسی","غیر رسمی خط","خلاصہ نویسی","درخواست"]),
  ]},
  "Grade 7": {"board":"Pakistan National Curriculum","units":[
    _u("نثر و نظم",["متن کی تفہیم و تجزیہ","شاعری کا تجزیہ","ادبی اصناف","کلاسیکی شاعری","جدید نثر"]),
    _u("قواعد",["جملے کی اقسام","فقرے","محاورے و ضرب الامثال","ہم معنی الفاظ","متضاد الفاظ"]),
    _u("تحریر",["رسمی خط","وضاحتی مضامین","تقریر","ڈائری نویسی","رپورٹ"]),
  ]},
  "Grade 8": {"board":"Pakistan National Curriculum","units":[
    _u("ادب",["کلاسیکی غزل: میرؔ، غالبؔ","اقبالؒ کا کلام","ترقی پسند ادب","افسانہ نگاری","انشائیہ"]),
    _u("قواعد",["صنعتِ بدیع: تشبیہ، استعارہ","علمِ عروض: بحریں","قوافی اور ردیف","ادبی اصطلاحات"]),
    _u("تحریر",["تنقیدی مضمون","تحقیقی مقالہ","ادبی خط","تقریر و مناظرہ","خبر نویسی"]),
  ]},
  "Grade 9": {"board":"Pakistan FBISE / Provincial Boards","units":[
    _u("نثر",["نثری اقتباسات کی تشریح","مضامین کا تجزیہ","نثری اصناف","اسلوبِ نویسی","اردو ادب کی تاریخ"]),
    _u("نظم",["غزل کی تشریح و تجزیہ","نظم کا تجزیہ","علامہ اقبالؒ: بانگِ درا","میرؔ اور غالبؔ","جدید شاعری"]),
    _u("قواعد و انشاء",["قواعد کا اطلاق","مضمون نویسی: مختلف اقسام","خط نویسی: رسمی و غیر رسمی","خلاصہ نویسی","درخواست و رپورٹ"]),
  ]},
  "Grade 10": {"board":"Pakistan FBISE / Provincial Boards","units":[
    _u("نثر و ادب",["اردو ادب کی تاریخ: جدید دور","ممتاز ادیب و شعراء","ادبی تحریکیں","تنقید کے اصول","جدید نثری اصناف"]),
    _u("شاعری",["کلیاتِ اقبال: منتخب کلام","غالبؔ کا دیوان: منتخب اشعار","دیگر کلاسیکی شعراء","جدید شاعری","تقابلی مطالعہ"]),
    _u("زبان و قواعد",["اعلیٰ قواعد کا اطلاق","انشاء پردازی: فنی پہلو","تنقیدی تحریر","ترجمہ","اردو صحافت"]),
  ]},
  "O Level": {"board":"Cambridge O Level Urdu (3247)","units":[
    _u("Reading & Comprehension",["Passage comprehension","Summary writing in Urdu","Directed writing","Vocabulary in context","Inferential and evaluative questions"]),
    _u("Writing",["Essay writing: various types","Formal letters","Narrative writing","Descriptive writing","Argumentative writing"]),
  ]},
  "A Level": {"board":"Cambridge A Level Urdu (9676)","units":[
    _u("Language Skills",["Advanced comprehension","Translation: Urdu to English","Critical analysis of texts","Register and style","Language variation in Pakistan"]),
    _u("Literature",["Classical poetry: detailed study","Modern prose","Drama: structure and themes","Short stories: technique","Literary criticism"]),
  ]},
}

# ─────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ZM Academy 📚",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────────
# CONSTANTS & LOOKUPS
# ─────────────────────────────────────────────────────────────────
SUBJECTS = {
    "Maths":           {"emoji": "🔢", "color": "#E8472A"},
    "Physics":         {"emoji": "⚡", "color": "#2563EB"},
    "Chemistry":       {"emoji": "🧪", "color": "#7C3AED"},
    "Biology":         {"emoji": "🌱", "color": "#059669"},
    "English":         {"emoji": "📖", "color": "#0891B2"},
    "Computer Science":{"emoji": "💻", "color": "#6D28D9"},
    "Urdu":            {"emoji": "🖊️", "color": "#B45309"},
}

LEVELS = [
    "Grade 1","Grade 2","Grade 3","Grade 4","Grade 5",
    "Grade 6","Grade 7","Grade 8","Grade 9","Grade 10",
    "O Level","A Level"
]

# Legacy compat mapping: Class 1-10 → Grade 1-10
_LEVEL_ALIAS = {f"Class {i}": f"Grade {i}" for i in range(1, 11)}

def normalise_level(grade):
    return _LEVEL_ALIAS.get(grade, grade)

def get_level_index(grade):
    grade = normalise_level(grade)
    try:
        return LEVELS.index(grade) if grade in LEVELS else 5
    except Exception:
        return 5

AVATARS = {
    "👦 Boy":"👦","👧 Girl":"👧","👨 Dad":"👨","👩 Mom":"👩",
    "👨‍🏫 Teacher":"👨‍🏫","🧑‍🚀 Astronaut":"🧑‍🚀",
    "🧑‍🔬 Scientist":"🧑‍🔬","🧑‍🎨 Artist":"🧑‍🎨"
}

IMAGE_STYLES = {
    "📐 Educational Diagram": "a clean labeled educational diagram with arrows, colorful sections, white background",
    "🎨 Cartoon":             "a bright fun cartoon illustration with cheerful bold colors suitable for students",
    "🎌 Anime Style":         "an anime-style illustration with vibrant colors, clean lines, expressive characters",
    "🤖 AI Art":              "a futuristic AI-generated digital art style with glowing elements and deep colors",
    "🔬 Realistic / Scientific": "a detailed realistic scientific illustration like a textbook diagram, accurate and labeled",
}

BADGES = [
    {"id":"first_q",  "icon":"🌟","name":"First Step",        "desc":"Asked first question",    "req": lambda s: s.get("total",0)>=1},
    {"id":"curious",  "icon":"🧠","name":"Curious Mind",      "desc":"Asked 5 questions",       "req": lambda s: s.get("total",0)>=5},
    {"id":"seeker",   "icon":"📚","name":"Knowledge Seeker",  "desc":"Asked 20 questions",      "req": lambda s: s.get("total",0)>=20},
    {"id":"maths",    "icon":"🔢","name":"Maths Master",      "desc":"10 Maths questions",      "req": lambda s: s.get("Maths",0)>=10},
    {"id":"physics",  "icon":"⚡","name":"Physics Pro",       "desc":"10 Physics questions",    "req": lambda s: s.get("Physics",0)>=10},
    {"id":"english",  "icon":"📖","name":"English Expert",    "desc":"10 English questions",    "req": lambda s: s.get("English",0)>=10},
    {"id":"urdu",     "icon":"🖊️","name":"Urdu Ustad",        "desc":"10 Urdu questions",       "req": lambda s: s.get("Urdu",0)>=10},
    {"id":"allround", "icon":"🏆","name":"All-Rounder",       "desc":"Studied 4+ subjects",     "req": lambda s: sum(1 for x in ["Maths","Physics","English","Urdu"] if s.get(x,0)>0)>=4},
    {"id":"artist",   "icon":"🎨","name":"Visual Learner",    "desc":"Generated 3 images",      "req": lambda s: s.get("images",0)>=3},
    {"id":"quiz_hero","icon":"🥇","name":"Quiz Champion",     "desc":"Completed 5 quizzes",     "req": lambda s: s.get("quizzes_done",0)>=5},
    {"id":"streak",   "icon":"🔥","name":"7-Day Streak",      "desc":"7 days in a row",         "req": lambda s: s.get("streak",0)>=7},
]

QUICK_PROMPTS = {
    "Maths":           ["Explain fractions with examples","Solve: 2x + 5 = 15","What is Pythagoras theorem?","How to calculate percentage?"],
    "Physics":         ["What are Newton's 3 laws?","How does electricity work?","What is gravity?","Difference between speed and velocity"],
    "Chemistry":       ["What is the periodic table?","Explain atomic structure","What are chemical bonds?","How do acids and bases work?"],
    "Biology":         ["Explain photosynthesis","What is DNA?","How does the heart work?","What is cell division?"],
    "English":         ["How to write a good essay?","Explain past and present tense","What are nouns and verbs?","How to improve vocabulary?"],
    "Computer Science":["What is an algorithm?","Explain loops in programming","What is a database?","How does the internet work?"],
    "Urdu":            ["اردو گرامر کی بنیادی باتیں","نظم اور نثر میں کیا فرق ہے؟","اچھا مضمون کیسے لکھیں؟","محاورے کیا ہوتے ہیں؟"],
}

CAMBRIDGE_SUBJECTS = {
    "Grade 6":  ["Mathematics","Physics","Chemistry","Biology","English","Computer Science","Urdu"],
    "Grade 7":  ["Mathematics","Physics","Chemistry","Biology","English","Computer Science","Urdu"],
    "Grade 8":  ["Mathematics","Physics","Chemistry","Biology","English","Computer Science","Urdu"],
    "Grade 9":  ["Mathematics","Physics","Chemistry","Biology","English","Computer Science","Urdu"],
    "Grade 10": ["Mathematics","Physics","Chemistry","Biology","English","Computer Science","Urdu"],
    "O Level":  ["Mathematics","Physics","Chemistry","Biology","English Language","Computer Science","Urdu"],
    "A Level":  ["Mathematics","Physics","Chemistry","Biology","English Language","Computer Science"],
}
for g in ["Grade 1","Grade 2","Grade 3","Grade 4","Grade 5"]:
    CAMBRIDGE_SUBJECTS[g] = ["Mathematics","English","Urdu","Science","Islamiyat"]

# ─────────────────────────────────────────────────────────────────
# DATA STORAGE
# ─────────────────────────────────────────────────────────────────
USERS_FILE    = "users.json"
HISTORY_FILE  = "history.json"
IMAGES_FILE   = "images.json"
GROUPS_FILE   = "groups.json"
HOMEWORK_FILE = "homework.json"

def load_json(filepath):
    cache_key = f"_cache_{filepath}"
    try:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            st.session_state[cache_key] = data
            return data
    except Exception:
        pass
    return st.session_state.get(cache_key, {})

def save_json(filepath, data):
    cache_key = f"_cache_{filepath}"
    st.session_state[cache_key] = data
    tmp = filepath + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, filepath)
    except Exception:
        try: os.remove(tmp)
        except Exception: pass

def hash_pw(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ─────────────────────────────────────────────────────────────────
# STATS & BADGES
# ─────────────────────────────────────────────────────────────────
DAILY_LIMITS = {"free":15, "basic":50, "premium":9999}

def init_stats():
    return {"total":0,"Maths":0,"Physics":0,"Chemistry":0,"Biology":0,
            "English":0,"Computer Science":0,"Urdu":0,
            "streak":0,"lastDate":"","images":0,"quizzes_done":0,
            "dailyQs":0,"dailyDate":"","study_dates":[]}

def get_daily_used(user):
    stats = user.get("stats", {})
    today = datetime.date.today().isoformat()
    if stats.get("dailyDate","") != today: return 0
    return stats.get("dailyQs", 0)

def check_daily_limit(user):
    plan  = user.get("plan","free")
    limit = DAILY_LIMITS.get(plan, 10)
    used  = get_daily_used(user)
    return used < limit, used, limit

def check_badges(user):
    earned   = user.get("badges", [])
    new_ones = []
    stats    = user.get("stats", {})
    for b in BADGES:
        if b["id"] not in earned and b["req"](stats):
            earned.append(b["id"])
            new_ones.append(b)
    user["badges"] = earned
    return user, new_ones

def bump_stats(subject_field=None, extra_field=None):
    users = load_json(USERS_FILE)
    email = st.session_state.user["email"]
    u     = users.get(email, st.session_state.user)
    s     = u.get("stats", init_stats())
    s["total"] = s.get("total", 0) + 1
    if subject_field: s[subject_field] = s.get(subject_field, 0) + 1
    if extra_field:   s[extra_field]   = s.get(extra_field, 0) + 1
    today = datetime.date.today().isoformat()
    yest  = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    if   s.get("lastDate","") == today: pass
    elif s.get("lastDate","") == yest:  s["streak"] = s.get("streak",0)+1
    else:                               s["streak"] = 1
    s["lastDate"] = today
    study_dates = s.get("study_dates", [])
    if today not in study_dates:
        study_dates.append(today)
        study_dates = study_dates[-60:]
    s["study_dates"] = study_dates
    if s.get("dailyDate","") != today:
        s["dailyQs"]   = 0
        s["dailyDate"] = today
    s["dailyQs"] = s.get("dailyQs",0)+1
    u["stats"] = s
    u, new_badges = check_badges(u)
    users[email] = u
    save_json(USERS_FILE, users)
    st.session_state.user = u
    for b in new_badges:
        st.toast(f"🏆 Badge Earned: {b['icon']} {b['name']}!", icon="🎉")

# ─────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────
defaults = {
    "logged_in": False, "user": None, "page": "home",
    "subject": "Maths", "level": "Grade 6",
    "chat_messages": [], "session_id": None,
    "quiz": None,
    "word_of_day": None, "wod_loaded": False,
    "syl_subject": "Maths", "syl_unit": None,
    "syl_curriculum": "Cambridge",
    "syl_grade": "Grade 8",
    "syl_subject_name": "Mathematics",
    "syl_custom_grade": "",
    "syl_custom_subject": "",
    "group_session": None,
    "group_player_idx": 0,
    "confirm_clear_hist": False,
    "mobile_hint_shown": False,
    # Online friends quiz room state
    "fq_room_id": None,
    "fq_role": None,
    "fq_last_q": 0,
    "fq_answered": {},
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────
# ANTHROPIC CLIENT
# ─────────────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    key = (st.secrets.get("ANTHROPIC_API_KEY","") or st.secrets.get("CLAUDE_API_KEY","") or os.environ.get("ANTHROPIC_API_KEY","") or os.environ.get("CLAUDE_API_KEY",""))
    if not key: return None
    return Anthropic(api_key=key)

client = get_client()

def call_ai(messages, system, max_tokens=1200):
    if not client:
        return "__API_KEY_MISSING__"
    try:
        r = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=max_tokens,
            system=system,
            messages=messages
        )
        text = r.content[0].text if r.content else ""
        return text if text.strip() else "__EMPTY_RESPONSE__"
    except Exception as e:
        return f"__API_ERROR__: {e}"

def call_ai_svg(messages, system):
    if not client:
        return "⚠️ API key not configured."
    try:
        r = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=4000,
            system=system,
            messages=messages
        )
        return r.content[0].text
    except Exception as e:
        return f"ERROR: {e}"

# ─────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600;9..40,700;9..40,800&family=DM+Serif+Display:ital@0;1&display=swap');

:root{
  --bg:        #F5F7FA;
  --surface:   #FFFFFF;
  --surface2:  #EEF2F7;
  --border:    #E4E8EE;
  --green:     #1C7C54;
  --green-mid: #25A870;
  --green-lt:  #34C77B;
  --green-bg:  #EBF7F1;
  --gold:      #C9A84C;
  --gold-lt:   #E8C96A;
  --crimson:   #DC3545;
  --blue:      #1B4FD8;
  --text:      #1A1D23;
  --text2:     #5A6070;
  --text3:     #9BA3B0;
  --white:     #FFFFFF;
  --shadow-sm: 0 1px 4px rgba(0,0,0,0.06);
  --shadow-md: 0 4px 16px rgba(0,0,0,0.09);
  --shadow-lg: 0 8px 32px rgba(0,0,0,0.12);
  --radius:    14px;
  --radius-sm: 10px;
  --radius-lg: 20px;
}

html,body,[class*="css"]{
  font-family:'DM Sans',system-ui,sans-serif !important;
  background:var(--bg) !important;
  color:var(--text) !important;
}
.main .block-container{
  padding-top:1.4rem !important; padding-bottom:4rem !important;
  max-width:980px !important;
  padding-left:1.8rem !important; padding-right:1.8rem !important;
  background:var(--bg) !important;
}
#MainMenu,footer,header{ visibility:hidden; }

@media(max-width:768px){
  .main .block-container{ padding-left:.7rem !important; padding-right:.7rem !important; }
  .stButton>button{ min-height:46px !important; font-size:13.5px !important; }
  .msg-user{ margin-left:4px !important; }
  .msg-bot{  margin-right:4px !important; }
  div[data-testid="column"]{ padding:2px !important; }
  .stTextInput>div>div>input{ font-size:16px !important; }
}

/* ── BUTTONS ────────────────────────────────────────── */
.stButton>button{
  background:var(--surface) !important;
  border:1.5px solid var(--border) !important;
  color:var(--text) !important;
  font-family:'DM Sans',sans-serif !important;
  font-weight:600 !important; font-size:13.5px !important;
  border-radius:var(--radius-sm) !important;
  padding:10px 18px !important;
  transition:all .18s ease !important;
  box-shadow:var(--shadow-sm) !important;
}
.stButton>button:hover{
  border-color:var(--green) !important;
  color:var(--green) !important;
  background:#F0FDF4 !important;
  box-shadow:var(--shadow-md) !important;
  transform:translateY(-1px) !important;
}
.stButton>button[kind="primary"]{
  background:var(--green) !important;
  color:#fff !important; border:none !important;
  box-shadow:0 4px 14px rgba(28,124,84,0.35) !important;
  font-weight:700 !important;
}
.stButton>button[kind="primary"]:hover{
  background:var(--green-mid) !important;
  box-shadow:0 6px 20px rgba(28,124,84,0.45) !important;
  transform:translateY(-2px) !important;
  color:#fff !important;
}

/* ── SIDEBAR ────────────────────────────────────────── */
[data-testid="stSidebar"]{
  background:#FFFFFF !important;
  border-right:1.5px solid var(--border) !important;
}
[data-testid="stSidebar"] *{ color:var(--text) !important; }
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] label{ color:var(--text2) !important; }

[data-testid="stSidebar"] .stButton>button{
  background:transparent !important;
  border:none !important;
  color:var(--text2) !important;
  font-weight:600 !important; font-size:13px !important;
  text-align:left !important;
  padding:9px 12px !important; border-radius:10px !important;
  margin-bottom:1px !important; width:100% !important;
  transition:background .15s,color .15s !important;
  box-shadow:none !important; transform:none !important;
}
[data-testid="stSidebar"] .stButton>button:hover{
  background:var(--bg) !important;
  color:var(--text) !important;
  transform:none !important;
}
[data-testid="stSidebar"] .stButton>button[kind="primary"]{
  background:var(--green-bg) !important;
  border:none !important;
  color:var(--green) !important;
  font-weight:700 !important;
  box-shadow:none !important;
  transform:none !important;
}

/* ── STAT CARDS ─────────────────────────────────────── */
.stat-card{
  background:var(--surface); border-radius:var(--radius);
  padding:18px 14px; text-align:center;
  box-shadow:var(--shadow-sm); border:1.5px solid var(--border);
  transition:box-shadow .18s,transform .18s;
  position:relative; overflow:hidden;
}
.stat-card::before{
  content:''; position:absolute; top:0; left:0; right:0; height:3px;
  background:var(--green); border-radius:var(--radius) var(--radius) 0 0;
}
.stat-card:hover{ box-shadow:var(--shadow-md); transform:translateY(-2px); }
.stat-num{ font-family:'DM Serif Display',serif; font-size:30px; font-weight:400; color:var(--green); }
.stat-lbl{ font-size:11px; color:var(--text3); margin-top:4px; font-weight:600; text-transform:uppercase; letter-spacing:.7px; }

/* ── HERO BANNER ────────────────────────────────────── */
.hero-banner{
  background:linear-gradient(130deg,#1C7C54 0%,#25A870 55%,#1B7A50 100%);
  border-radius:var(--radius-lg); padding:26px 28px; margin-bottom:22px;
  color:#fff; position:relative; overflow:hidden;
  box-shadow:0 6px 24px rgba(28,124,84,0.22);
}
.hero-banner::before{
  content:''; position:absolute; top:-50px; right:-30px;
  width:200px; height:200px; border-radius:50%;
  background:rgba(255,255,255,0.06);
}
.hero-banner::after{
  content:''; position:absolute; bottom:-60px; right:140px;
  width:130px; height:130px; border-radius:50%;
  background:rgba(201,168,76,0.10);
}

/* ── SECTION HEADER ─────────────────────────────────── */
.section-header{
  background:var(--surface); color:var(--text);
  border-radius:var(--radius); padding:14px 20px; margin-bottom:18px;
  font-family:'DM Serif Display',serif; font-size:21px; font-weight:400;
  border-left:4px solid var(--green);
  border-top:1.5px solid var(--border);
  border-right:1.5px solid var(--border);
  border-bottom:1.5px solid var(--border);
  box-shadow:var(--shadow-sm); letter-spacing:-.2px;
}
.section-header.orange{ border-left-color:#DC3545; }
.section-header.gold{   border-left-color:var(--gold); }
.section-header.blue{   border-left-color:var(--blue); }
.section-header.purple{ border-left-color:#6D28D9; }

/* ── SUBJECT CARDS ─────────────────────────────────── */
.subj-card{
  background:var(--surface); border-radius:var(--radius);
  padding:16px 12px; text-align:center;
  border:1.5px solid var(--border); box-shadow:var(--shadow-sm);
  transition:all .18s ease; cursor:pointer;
}
.subj-card:hover{ transform:translateY(-3px); box-shadow:var(--shadow-md); }
.subj-emoji{ font-size:28px; display:block; margin-bottom:6px; }
.subj-name{ font-size:12px; font-weight:700; color:var(--text); }
.subj-count{ font-size:10px; color:var(--text3); font-weight:500; margin-top:2px; }
.subj-prog{ margin-top:8px; background:#EDF0F5; border-radius:99px; height:4px; overflow:hidden; }
.subj-prog-fill{ height:4px; border-radius:99px; }

/* ── DAILY CHALLENGE ────────────────────────────────── */
.daily-challenge{
  background:linear-gradient(135deg,#1A1D23,#2D3748);
  border-radius:var(--radius-lg); padding:18px 22px; margin-bottom:20px;
  color:#fff; border:1px solid rgba(201,168,76,0.2);
  box-shadow:var(--shadow-md);
}

/* ── FEATURE / QUICK-START CARD ─────────────────────── */
.feature-card{
  background:var(--surface); border-radius:var(--radius);
  padding:14px 16px; border:1.5px solid var(--border);
  box-shadow:var(--shadow-sm); margin-bottom:8px; color:var(--text);
  transition:all .18s ease;
}
.feature-card:hover{ border-color:var(--green); box-shadow:var(--shadow-md); transform:translateX(2px); }

/* ── HIST CARD ──────────────────────────────────────── */
.hist-card{
  background:var(--surface); border-radius:var(--radius);
  padding:14px 16px; box-shadow:var(--shadow-sm);
  border:1.5px solid var(--border); margin-bottom:8px;
}

/* ── CHAT MESSAGES ──────────────────────────────────── */
.msg-user{
  background:var(--green); color:#fff;
  border-radius:18px 18px 4px 18px; padding:12px 16px;
  margin:5px 0 5px 48px; font-size:14px; line-height:1.7;
  box-shadow:0 3px 12px rgba(28,124,84,0.2);
}
.msg-bot{
  background:var(--surface); color:var(--text);
  border-radius:18px 18px 18px 4px; padding:12px 16px;
  margin:5px 48px 5px 0; font-size:14px; line-height:1.75;
  box-shadow:var(--shadow-sm); border:1.5px solid var(--border);
}
.msg-lbl{ font-size:11px; color:var(--text3); margin-bottom:3px; font-weight:600; }
.msg-lbl-r{ text-align:right; }

/* ── PROGRESS BAR ───────────────────────────────────── */
.prog-bar{ background:var(--surface2); border-radius:99px; height:9px; overflow:hidden; margin-bottom:4px; }
.prog-fill{ height:100%; border-radius:99px; transition:width .5s ease; }

/* ── BADGE CARD ─────────────────────────────────────── */
.badge-card{
  background:var(--surface); border:1.5px solid var(--border);
  border-radius:var(--radius); padding:14px 10px; text-align:center;
  box-shadow:var(--shadow-sm); transition:transform .18s,box-shadow .18s;
}
.badge-card:hover{ transform:translateY(-3px); box-shadow:var(--shadow-md); }
.badge-locked{ opacity:.35; filter:grayscale(1); }
.badge-icon{ font-size:28px; display:block; }
.badge-name{ font-size:12px; font-weight:700; color:var(--text); margin-top:6px; }
.badge-desc{ font-size:10px; color:var(--text3); margin-top:2px; }

/* ── WORD CARD ──────────────────────────────────────── */
.word-card{
  background:linear-gradient(135deg,#1A1D23 0%,#2D3748 100%);
  border-radius:var(--radius); padding:20px 22px; margin-bottom:16px;
  color:#fff; border:1px solid rgba(201,168,76,0.2); box-shadow:var(--shadow-md);
  position:relative; overflow:hidden;
}

/* ── REMINDER ───────────────────────────────────────── */
.reminder{
  background:linear-gradient(135deg,#FFFDF0,#FFF8DC);
  border:1.5px solid rgba(201,168,76,0.35); border-radius:var(--radius);
  padding:12px 16px; margin-bottom:14px; font-size:13px; color:var(--text);
}

/* ── LEADERBOARD ────────────────────────────────────── */
.lb-row{
  display:flex; align-items:center; gap:12px; padding:12px 16px;
  background:var(--surface); border-radius:var(--radius); margin-bottom:6px;
  box-shadow:var(--shadow-sm); border:1.5px solid var(--border); color:var(--text);
  transition:box-shadow .18s,transform .18s;
}
.lb-row:hover{ box-shadow:var(--shadow-md); transform:translateX(3px); }
.lb-rank{ font-size:20px; font-weight:900; width:30px; text-align:center; }
.lb-name{ flex:1; font-weight:700; font-size:14px; }
.lb-score{ font-weight:800; font-size:16px; color:var(--green); font-family:'DM Serif Display',serif; }

/* ── SYLLABUS ───────────────────────────────────────── */
.syl-step{
  background:var(--surface); border-radius:var(--radius); padding:14px 18px;
  margin-bottom:10px; border:1.5px solid var(--border); box-shadow:var(--shadow-sm); color:var(--text);
}
.syl-step-title{ font-size:11px; font-weight:700; color:var(--green); text-transform:uppercase; letter-spacing:1px; margin-bottom:8px; }
.topic-chip{ display:inline-block; border-radius:20px; padding:4px 11px; font-size:11px; font-weight:600; margin:3px 3px 3px 0; }

/* ── FORM INPUTS ────────────────────────────────────── */
[data-testid="stSelectbox"]>div>div{
  background:var(--surface) !important; border:1.5px solid var(--border) !important;
  border-radius:var(--radius-sm) !important; color:var(--text) !important;
}
[data-testid="stSelectbox"]>div>div>div{ color:var(--text) !important; font-weight:600 !important; }
[data-baseweb="popover"],[data-baseweb="menu"],[role="listbox"]{
  background:var(--surface) !important; border:1.5px solid var(--border) !important;
  border-radius:var(--radius) !important; box-shadow:var(--shadow-lg) !important;
}
[role="option"]{ color:var(--text) !important; background:var(--surface) !important; font-size:13.5px !important; padding:9px 14px !important; }
[role="option"]:hover,[role="option"][aria-selected="true"]{
  background:var(--green-bg) !important; color:var(--green) !important; font-weight:700 !important;
}
.stTextInput>div>div>input,
.stTextArea>div>div>textarea{
  border-radius:var(--radius-sm) !important; border:1.5px solid var(--border) !important;
  color:var(--text) !important; background:var(--surface) !important;
  font-family:'DM Sans',sans-serif !important;
}
.stTextInput>div>div>input:focus,
.stTextArea>div>div>textarea:focus{
  border-color:var(--green) !important;
  box-shadow:0 0 0 3px rgba(28,124,84,0.10) !important;
}
label,[data-testid="stLabel"]>label{ color:var(--text) !important; font-weight:600 !important; font-size:13px !important; }

/* ── TABS ───────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"]{
  background:var(--surface2) !important; border-radius:var(--radius-sm) !important;
  padding:4px !important; border:1.5px solid var(--border) !important; gap:3px !important;
}
.stTabs [data-baseweb="tab"]{
  background:transparent !important; color:var(--text2) !important;
  font-weight:600 !important; font-size:13px !important;
  border-radius:8px !important; padding:7px 14px !important; border:none !important;
}
.stTabs [aria-selected="true"]{
  background:var(--surface) !important; color:var(--green) !important;
  box-shadow:var(--shadow-sm) !important; font-weight:700 !important;
}

/* ── EXPANDER ───────────────────────────────────────── */
[data-testid="stExpander"]{
  background:var(--surface) !important; border:1.5px solid var(--border) !important;
  border-radius:var(--radius-sm) !important; margin-bottom:5px !important;
}
[data-testid="stExpander"] summary{ font-weight:600 !important; color:var(--text) !important; }

/* ── METRICS ────────────────────────────────────────── */
[data-testid="stMetricValue"]{ color:var(--green) !important; font-family:'DM Serif Display',serif !important; }
[data-testid="stMetricLabel"]{ color:var(--text2) !important; font-weight:600 !important; }

/* ── ALERTS ─────────────────────────────────────────── */
[data-testid="stAlert"]{ border-radius:var(--radius-sm) !important; border-left-width:4px !important; }

/* ── RADIO / CHECKBOX ───────────────────────────────── */
.stRadio label,[data-testid="stRadio"] label{ color:var(--text) !important; font-weight:600 !important; }
.stCheckbox label{ color:var(--text) !important; font-weight:600 !important; }

/* ── SCROLLBAR ──────────────────────────────────────── */
::-webkit-scrollbar{ width:5px; height:5px; }
::-webkit-scrollbar-track{ background:var(--bg); }
::-webkit-scrollbar-thumb{ background:rgba(28,124,84,0.2); border-radius:99px; }
::-webkit-scrollbar-thumb:hover{ background:rgba(28,124,84,0.4); }
</style>
""", unsafe_allow_html=True)



# ─────────────────────────────────────────────────────────────────
# AUTH PAGE
# ─────────────────────────────────────────────────────────────────
def page_auth():
    st.markdown("""
    <style>
    .main .block-container{ max-width:480px !important; padding-top:2rem !important; }
    [data-testid="stForm"]{ background:var(--surface) !important; border-radius:20px !important; padding:24px !important; border:1.5px solid var(--border) !important; box-shadow:var(--shadow-lg) !important; }
    </style>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;padding:32px 0 24px">
        <div style="display:inline-flex;align-items:center;justify-content:center;
            width:80px;height:80px;border-radius:24px;margin-bottom:16px;
            background:linear-gradient(135deg,#0D6E3F,#1A8C50);
            box-shadow:0 8px 32px rgba(13,110,63,0.4)">
            <span style="font-size:40px;line-height:1">📚</span>
        </div>
        <h1 style="font-family:'Sora',sans-serif;font-size:32px;font-weight:900;
            color:#0D1F0D;margin:0 0 6px;letter-spacing:-1px">ZM Academy</h1>
        <p style="color:#3D5C3D;font-size:14px;font-weight:600;margin:0">
            🇵🇰 Pakistan's <b style="color:#0D6E3F">#1</b> AI-Powered Education Platform
        </p>
        <div style="display:flex;justify-content:center;gap:8px;margin-top:10px;flex-wrap:wrap">
            <span style="background:rgba(13,110,63,0.08);color:#0D6E3F;padding:3px 12px;
                border-radius:99px;font-size:11px;font-weight:700;border:1px solid rgba(13,110,63,0.15)">
                Grades 1-10</span>
            <span style="background:rgba(13,110,63,0.08);color:#0D6E3F;padding:3px 12px;
                border-radius:99px;font-size:11px;font-weight:700;border:1px solid rgba(13,110,63,0.15)">
                O Level</span>
            <span style="background:rgba(13,110,63,0.08);color:#0D6E3F;padding:3px 12px;
                border-radius:99px;font-size:11px;font-weight:700;border:1px solid rgba(13,110,63,0.15)">
                A Level</span>
            <span style="background:rgba(201,168,76,0.15);color:#7A5C00;padding:3px 12px;
                border-radius:99px;font-size:11px;font-weight:700;border:1px solid rgba(201,168,76,0.25)">
                🤖 AI Powered</span>
        </div>
    </div>""", unsafe_allow_html=True)

    tab_login, tab_signup, tab_forgot = st.tabs(["🔑  Login","✨  Sign Up","🔓  Reset"])

    with tab_login:
        with st.form("login_form"):
            email    = st.text_input("📧 Email", placeholder="you@example.com")
            password = st.text_input("🔒 Password", type="password")
            if st.form_submit_button("Login to ZM Academy →", use_container_width=True, type="primary"):
                users = load_json(USERS_FILE)
                if email in users and users[email]["password"] == hash_pw(password):
                    users[email]["last_login"] = datetime.date.today().isoformat()
                    if "plan" not in users[email]: users[email]["plan"] = "free"
                    save_json(USERS_FILE, users)
                    st.session_state.logged_in = True
                    st.session_state.user      = users[email]
                    st.success("Welcome back! 🎉"); time.sleep(0.5); st.rerun()
                else:
                    st.error("⚠️ Incorrect email or password.")

    with tab_signup:
        with st.form("signup_form"):
            name   = st.text_input("👤 Full Name", placeholder="Ahmed Khan")
            email2 = st.text_input("📧 Email", placeholder="you@example.com")
            avatar = st.selectbox("🧑 Choose Avatar", list(AVATARS.keys()))
            grade  = st.selectbox("🏫 Grade", ["-- Select --"]+LEVELS)
            pw     = st.text_input("🔒 Password", type="password", placeholder="Min 6 characters")
            pw2    = st.text_input("🔒 Confirm Password", type="password")
            if st.form_submit_button("Create My Account →", use_container_width=True, type="primary"):
                users = load_json(USERS_FILE)
                if not name or not email2 or not pw:   st.error("Please fill all required fields.")
                elif len(pw) < 6:                      st.error("Password must be at least 6 characters.")
                elif pw != pw2:                        st.error("Passwords don't match.")
                elif email2 in users:                  st.error("Email already registered.")
                else:
                    new_user = {
                        "name": name.strip(), "email": email2.strip(),
                        "password": hash_pw(pw),
                        "role": "student",
                        "avatar": AVATARS[avatar],
                        "grade": grade if grade != "-- Select --" else "Grade 6",
                        "joined": datetime.date.today().isoformat(),
                        "plan": "free", "stats": init_stats(), "badges": [],
                        "studied_topics": {}, "is_new": True
                    }
                    users[email2] = new_user
                    save_json(USERS_FILE, users)
                    st.session_state.logged_in = True
                    st.session_state.user = new_user
                    st.success("Account created! Welcome 🎉"); time.sleep(0.5); st.rerun()

    with tab_forgot:
        st.markdown("""
        <div style="background:rgba(13,110,63,0.06);border-radius:10px;padding:12px 14px;
            font-size:13px;color:#0D6E3F;margin-bottom:14px;border:1px solid rgba(13,110,63,0.12)">
            🔒 Enter your email and a new password to reset your account.
        </div>""", unsafe_allow_html=True)
        with st.form("forgot_form"):
            fp_email = st.text_input("📧 Your registered email")
            fp_new   = st.text_input("🔒 New Password", type="password")
            fp_new2  = st.text_input("🔒 Confirm New Password", type="password")
            if st.form_submit_button("Reset Password →", use_container_width=True, type="primary"):
                users = load_json(USERS_FILE)
                if fp_email not in users:    st.error("⚠️ Email not found.")
                elif len(fp_new) < 6:        st.error("Min 6 characters.")
                elif fp_new != fp_new2:      st.error("Passwords don't match.")
                else:
                    users[fp_email]["password"] = hash_pw(fp_new)
                    save_json(USERS_FILE, users)
                    st.success("✅ Password reset! You can now login.")

    st.markdown("""
    <p style="text-align:center;color:#7A9A7A;font-size:11px;margin-top:20px;font-weight:600">
        🔒 Secure &nbsp;·&nbsp; 🆓 Free to use &nbsp;·&nbsp; 🇵🇰 Pakistan National Curriculum
    </p>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────

def render_sidebar():
    u    = st.session_state.user
    role = u.get("role", "student")
    stats = u.get("stats", {})

    ROLE_OPTIONS  = ["Student 🎒","Teacher 👨‍🏫","Parent 👨‍👩‍👦","Admin 🛡️"]
    ROLE_MAP      = {"Student 🎒":"student","Teacher 👨‍🏫":"teacher","Parent 👨‍👩‍👦":"parent","Admin 🛡️":"admin"}
    ROLE_REVERSE  = {v:k for k,v in ROLE_MAP.items()}
    cur_role_lbl  = ROLE_REVERSE.get(u.get("role","student"), "Student 🎒")
    cur_role_idx  = ROLE_OPTIONS.index(cur_role_lbl) if cur_role_lbl in ROLE_OPTIONS else 0

    with st.sidebar:
        # Logo
        st.markdown(
            "<div style=\"display:flex;align-items:center;gap:10px;"
            "padding:16px 14px 14px;"
            "border-bottom:1.5px solid #E4E8EE;\">"
            "<div style=\"width:36px;height:36px;border-radius:10px;flex-shrink:0;"
            "background:#1C7C54;"
            "display:flex;align-items:center;justify-content:center;font-size:20px;\">📚</div>"
            "<div>"
            "<div style=\"font-family:'DM Serif Display',serif;font-size:17px;"
            "color:#1C7C54;line-height:1.1\">ZM Academy</div>"
            "<div style=\"font-size:9px;color:#9BA3B0;font-weight:700;"
            "letter-spacing:.8px;text-transform:uppercase\">🇵🇰 Pakistan's AI Tutor</div>"
            "</div></div>",
            unsafe_allow_html=True
        )

        # User card
        xp_total = stats.get("total", 0) * 10
        xp_level = (xp_total // 500) + 1
        xp_pct   = min((xp_total % 500) / 5, 100)
        streak   = stats.get("streak", 0)
        st.markdown(
            f"<div style=\"padding:14px 14px 10px;border-bottom:1.5px solid #E4E8EE;\">"
            f"<div style=\"display:flex;align-items:center;gap:10px;margin-bottom:10px\">"
            f"<div style=\"width:42px;height:42px;border-radius:50%;flex-shrink:0;"
            f"background:#EBF7F1;border:2px solid #1C7C54;"
            f"display:flex;align-items:center;justify-content:center;font-size:24px;\">"
            f"{u.get('avatar','👦')}</div>"
            f"<div style=\"min-width:0\">"
            f"<div style=\"font-weight:700;font-size:13px;color:#1A1D23;\">{u['name']}</div>"
            f"<div style=\"font-size:11px;color:#9BA3B0;font-weight:500;margin-top:1px\">"
            f"{u.get('grade','')} · Lv.{xp_level}</div>"
            f"</div></div>"
            f"<div style=\"background:#EDF0F5;border-radius:99px;height:5px;overflow:hidden;margin-bottom:3px\">"
            f"<div style=\"width:{xp_pct:.0f}%;height:5px;border-radius:99px;background:#1C7C54\"></div></div>"
            f"<div style=\"display:flex;justify-content:space-between;font-size:10px;"
            f"color:#9BA3B0;font-weight:600\">"
            f"<span>{xp_total} XP</span><span>Lv.{xp_level+1} at {xp_level*500} XP</span>"
            f"</div></div>",
            unsafe_allow_html=True
        )

        # Streak
        if streak > 0:
            st.markdown(
                f"<div style=\"margin:10px 8px 0;background:linear-gradient(135deg,#FFF3E0,#FFF8EC);"
                f"border:1.5px solid #FFD08A;border-radius:10px;padding:8px 12px;"
                f"display:flex;align-items:center;gap:8px\">"
                f"<div><div style=\"font-size:8px;font-weight:800;color:#92400E;"
                f"letter-spacing:.8px;text-transform:uppercase\">🔥 Streak</div>"
                f"<div style=\"font-family:'DM Serif Display',serif;font-size:22px;"
                f"color:#E8770A;line-height:1\">{streak}</div></div>"
                f"<div style=\"font-size:11px;color:#92400E;font-weight:600;line-height:1.4\">"
                f"day{'s' if streak!=1 else ''} in a row!</div></div>",
                unsafe_allow_html=True
            )

        # Role selector
        st.markdown("<div style=\"padding:8px 8px 0\">", unsafe_allow_html=True)
        new_role_lbl = st.selectbox(
            "Role", ROLE_OPTIONS, index=cur_role_idx,
            key="sidebar_role_select", label_visibility="collapsed"
        )
        st.markdown("</div>", unsafe_allow_html=True)

        if ROLE_MAP[new_role_lbl] != u.get("role","student"):
            users_tmp = load_json(USERS_FILE)
            u["role"] = ROLE_MAP[new_role_lbl]
            users_tmp[u["email"]]["role"] = ROLE_MAP[new_role_lbl]
            save_json(USERS_FILE, users_tmp)
            st.session_state.user = u
            role = ROLE_MAP[new_role_lbl]
            st.rerun()
        else:
            role = u.get("role","student")

        cur = st.session_state.page

        def nav_btn(icon, label, key, uid=""):
            btn_type = "primary" if cur == key else "secondary"
            if st.button(f"{icon}  {label}", key=f"nav_{key}{uid}",
                         use_container_width=True, type=btn_type):
                st.session_state.page = key; st.rerun()

        def section_label(text):
            st.markdown(
                f"<div style=\"font-size:9px;font-weight:800;color:#9BA3B0;"
                f"text-transform:uppercase;letter-spacing:1.3px;"
                f"padding:14px 12px 4px;\">{text}</div>",
                unsafe_allow_html=True
            )

        nav_btn("🏠", "Home",            "home")
        nav_btn("📚", "Syllabus",        "syllabus")
        nav_btn("💬", "Chat Tutor",      "chat")
        nav_btn("📝", "Practice Quiz",   "quiz")
        nav_btn("👥", "Friendz Quiz",    "friends")
        nav_btn("🎨", "Image Generator", "image")
        nav_btn("🕐", "Chat History",    "history")
        nav_btn("🏆", "Badges",          "badges")

        if role in ("teacher","admin"):
            section_label("🛡️  Admin")
            nav_btn("📊", "Student Performance", "admin")
            if role == "teacher":
                nav_btn("📋", "Create Homework", "homework")

        nav_btn("👤", "Profile", "profile")

        # ── My Progress — footer section ─────────────────────────
        st.markdown(
            "<div style=\"margin:10px 0 0;border-top:1px solid #E4E8EE;"
            "padding-top:6px\"></div>",
            unsafe_allow_html=True
        )
        nav_btn("📈", "My Progress", "progress")

        # Mini stats row
        st.markdown(
            f"<div style=\"margin:12px 8px 0;background:#F5F7FA;border-radius:10px;"
            f"border:1.5px solid #E4E8EE;padding:10px;"
            f"display:flex;justify-content:space-around;text-align:center\">"
            f"<div><div style=\"font-family:'DM Serif Display',serif;font-size:18px;"
            f"color:#1C7C54\">{stats.get('total',0)}</div>"
            f"<div style=\"font-size:9px;color:#9BA3B0;font-weight:700;"
            f"text-transform:uppercase;letter-spacing:.6px\">Qs</div></div>"
            f"<div style=\"width:1px;background:#E4E8EE\"></div>"
            f"<div><div style=\"font-family:'DM Serif Display',serif;font-size:18px;"
            f"color:#1C7C54\">{len(u.get('badges',[]))}</div>"
            f"<div style=\"font-size:9px;color:#9BA3B0;font-weight:700;"
            f"text-transform:uppercase;letter-spacing:.6px\">Badges</div></div>"
            f"<div style=\"width:1px;background:#E4E8EE\"></div>"
            f"<div><div style=\"font-family:'DM Serif Display',serif;font-size:18px;"
            f"color:#1C7C54\">{stats.get('quizzes_done',0)}</div>"
            f"<div style=\"font-size:9px;color:#9BA3B0;font-weight:700;"
            f"text-transform:uppercase;letter-spacing:.6px\">Quizzes</div></div>"
            f"</div>",
            unsafe_allow_html=True
        )

        # Upgrade pill
        st.markdown(
            "<div style=\"margin:8px 8px 0;background:linear-gradient(135deg,#EBF7F1,#F0FAF5);"
            "border:1.5px solid #C8EAD8;border-radius:10px;padding:10px 12px\">"
            "<div style=\"font-size:12px;font-weight:800;color:#1C7C54\">⭐ Upgrade to Pro</div>"
            "<div style=\"font-size:10px;color:#5A6070;margin-top:2px\">"
            "Unlimited AI · PDF Export · Rs.500/mo</div></div>",
            unsafe_allow_html=True
        )

        st.markdown("<div style=\"height:6px\"></div>", unsafe_allow_html=True)
        if st.button("🚪  Logout", key="logout_btn", use_container_width=True):
            for k in list(defaults.keys()):
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()




def page_home():
    u      = st.session_state.user
    h      = datetime.datetime.now().hour
    greet  = "Good morning" if h < 12 else "Good afternoon" if h < 17 else "Good evening"
    role   = u.get("role","student")
    stats  = {**init_stats(), **u.get("stats",{})}
    streak = stats.get("streak", 0)
    total  = stats.get("total", 0)
    today_str = datetime.date.today().isoformat()
    last_date = stats.get("lastDate","")

    # ── Onboarding ────────────────────────────────────────────
    if u.get("is_new") and not st.session_state.get("onboarding_done"):
        step  = st.session_state.get("onboard_step", 1)
        steps = [
            {"emoji":"🎓", "title":"Welcome to ZM Academy!",
             "body":"Pakistan's <b>AI study app</b> for every grade.<br><br>Your AI tutor <b>Ustad</b> is here to help you learn!",
             "btn":"Next →"},
            {"emoji":"💬", "title":"What can you do here?",
             "body":"💬 <b>Ask Ustad</b> any question<br>📝 <b>Take a Quiz</b> to practise<br>📚 <b>Browse Syllabus</b> topics<br>🎨 <b>Generate Diagrams</b> with AI",
             "btn":"Next →"},
            {"emoji":"🏆", "title":"Earn Badges!",
             "body":"Study every day to keep your 🔥 streak alive.<br><br>Collect badges and beat your friends on the leaderboard!",
             "btn":"🚀 Let's Start!"},
        ]
        s = steps[step-1]
        _, col_c, _ = st.columns([1,2,1])
        with col_c:
            dots_html = "".join(
                "<span style=\"display:inline-block;width:9px;height:9px;border-radius:50%;"
                + f"background:{'#1C7C54' if i+1==step else '#E4E8EE'};margin:0 4px\"></span>"
                for i in range(3)
            )
            st.markdown(
                "<div style=\"background:#fff;border-radius:24px;padding:36px 28px;"
                "margin-top:24px;text-align:center;border:1.5px solid #E4E8EE;"
                "box-shadow:0 8px 32px rgba(0,0,0,0.08)\">"
                f"<div style=\"margin-bottom:16px\">{dots_html}</div>"
                f"<div style=\"font-size:60px;margin-bottom:16px\">{s['emoji']}</div>"
                "<div style=\"font-family:'DM Serif Display',serif;font-size:24px;"
                f"color:#1A1D23;margin-bottom:14px\">{s['title']}</div>"
                f"<div style=\"font-size:15px;color:#5A6070;line-height:1.9\">{s['body']}</div>"
                "</div>",
                unsafe_allow_html=True
            )
            st.markdown("<div style=\"height:14px\"></div>", unsafe_allow_html=True)
            if st.button(s["btn"], use_container_width=True, type="primary", key=f"ob_{step}"):
                if step < 3:
                    st.session_state.onboard_step = step+1; st.rerun()
                else:
                    users = load_json(USERS_FILE)
                    if u["email"] in users:
                        users[u["email"]]["is_new"] = False
                        save_json(USERS_FILE, users)
                        st.session_state.user = users[u["email"]]
                    st.session_state.onboarding_done = True; st.rerun()
            if step > 1 and st.button("← Back", key=f"ob_back_{step}", use_container_width=True):
                st.session_state.onboard_step = step-1; st.rerun()
            if st.button("Skip intro", key="skip_ob", use_container_width=True):
                users = load_json(USERS_FILE)
                if u["email"] in users:
                    users[u["email"]]["is_new"] = False
                    save_json(USERS_FILE, users)
                    st.session_state.user = users[u["email"]]
                st.session_state.onboarding_done = True; st.rerun()
        return

    # ── Mobile hint ───────────────────────────────────────────
    if not st.session_state.get("mobile_hint_shown", False):
        st.info("📱 **On mobile?** Tap the **☰** at top-left to open the menu!", icon="📱")
        st.session_state.mobile_hint_shown = True

    # ── GREETING CARD ─────────────────────────────────────────
    first_name = u["name"].split()[0]
    grade_lbl  = u.get("grade","")
    streak_txt = f"🔥 {streak} day streak!" if streak >= 2 else ("🔥 Keep going!" if streak == 1 else "Start your streak today!")
    reminder   = last_date and last_date != today_str

    st.markdown(
        "<div style=\"background:linear-gradient(130deg,#1C7C54 0%,#25A870 100%);"
        "border-radius:20px;padding:28px 28px 24px;"
        "margin-bottom:20px;color:#fff;position:relative;overflow:hidden\">"
        "<div style=\"position:absolute;top:-40px;right:-40px;width:160px;height:160px;"
        "border-radius:50%;background:rgba(255,255,255,0.06)\"></div>"
        "<div style=\"position:absolute;bottom:-50px;right:100px;width:100px;height:100px;"
        "border-radius:50%;background:rgba(201,168,76,0.10)\"></div>"
        "<div style=\"position:relative;z-index:1\">"
        f"<div style=\"font-size:34px;margin-bottom:6px\">{u.get('avatar','👦')}</div>"
        f"<div style=\"font-size:13px;color:rgba(255,255,255,0.7);font-weight:600;margin-bottom:4px\">{greet}!</div>"
        f"<div style=\"font-family:'DM Serif Display',serif;font-size:28px;color:#fff;line-height:1.2;margin-bottom:10px\">"
        f"Hello, {first_name}! 👋</div>"
        "<div style=\"display:flex;align-items:center;gap:12px;flex-wrap:wrap\">"
        f"<span style=\"background:rgba(255,255,255,0.15);border-radius:99px;padding:5px 14px;"
        f"font-size:12px;font-weight:700\">📚 {grade_lbl}</span>"
        f"<span style=\"background:rgba(255,255,255,0.15);border-radius:99px;padding:5px 14px;"
        f"font-size:12px;font-weight:700\">{streak_txt}</span>"
        f"<span style=\"background:rgba(255,255,255,0.15);border-radius:99px;padding:5px 14px;"
        f"font-size:12px;font-weight:700\">⭐ {total} questions</span>"
        "</div>"
        "</div></div>",
        unsafe_allow_html=True
    )

    if reminder:
        st.markdown(
            "<div style=\"background:#FFF9E6;border:1.5px solid #FBBF24;border-radius:12px;"
            "padding:12px 16px;margin-bottom:16px;font-size:14px;color:#92400E;font-weight:600\">"
            "⏰ You haven't studied today — even 10 minutes counts! 💪</div>",
            unsafe_allow_html=True
        )

    # ── WHAT DO YOU WANT TO DO? (4 big buttons) ───────────────
    st.markdown(
        "<div style=\"font-family:'DM Serif Display',serif;font-size:22px;"
        "color:#1A1D23;margin-bottom:14px\">What do you want to do?</div>",
        unsafe_allow_html=True
    )

    # Scoped CSS for big action cards
    st.markdown("""
    <style>
    .action-grid-btn .stButton > button {
        min-height: 90px !important;
        font-size: 15px !important;
        font-weight: 700 !important;
        border-radius: 16px !important;
        white-space: normal !important;
        word-break: break-word !important;
        line-height: 1.4 !important;
        border: 1.5px solid #E4E8EE !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
    }
    .action-grid-btn .stButton > button:hover {
        border-color: #1C7C54 !important;
        color: #1C7C54 !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 6px 20px rgba(28,124,84,0.12) !important;
    }
    </style>
    <div class="action-grid-btn">
    """, unsafe_allow_html=True)

    action_cols = st.columns(4)
    actions = [
        ("💬", "Ask Ustad\nAI Chat Tutor",     "chat"),
        ("📝", "Take a Quiz\nPractise & Test",  "quiz"),
        ("📚", "My Syllabus\nBrowse Topics",    "syllabus"),
        ("🎨", "Draw It!\nAI Diagrams",         "image"),
    ]
    for col, (icon, label, dest) in zip(action_cols, actions):
        with col:
            if st.button(f"{icon}\n{label}", key=f"act_{dest}", use_container_width=True):
                st.session_state.page = dest; st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # ── MY SUBJECTS ───────────────────────────────────────────
    st.markdown("<div style=\"height:8px\"></div>", unsafe_allow_html=True)
    st.markdown(
        "<div style=\"font-family:'DM Serif Display',serif;font-size:22px;"
        "color:#1A1D23;margin-bottom:14px\">📖 Pick a Subject</div>",
        unsafe_allow_html=True
    )

    SUBJ_META = {
        "Maths":            ("🔢","#E8472A"),
        "Physics":          ("⚡","#1B4FD8"),
        "Chemistry":        ("🧪","#7C3AED"),
        "Biology":          ("🌿","#059669"),
        "English":          ("📖","#D97706"),
        "Computer Science": ("💻","#0891B2"),
        "Urdu":             ("🖊️","#BE185D"),
    }

    subj_cols = st.columns(len(SUBJ_META))
    for idx, (sname, (semoji, scolor)) in enumerate(SUBJ_META.items()):
        sq = stats.get(sname, 0)
        with subj_cols[idx]:
            st.markdown(
                f"<div style=\"background:#fff;border-radius:14px;padding:16px 10px;"
                f"text-align:center;border:1.5px solid #E4E8EE;"
                f"border-top:4px solid {scolor};"
                f"box-shadow:0 2px 8px rgba(0,0,0,0.04);"
                f"transition:all .18s ease;cursor:pointer\">"
                f"<div style=\"font-size:30px;margin-bottom:8px\">{semoji}</div>"
                f"<div style=\"font-size:12px;font-weight:700;color:#1A1D23;margin-bottom:4px\">{sname}</div>"
                f"<div style=\"font-size:10px;color:#9BA3B0;font-weight:500\">{sq} Qs done</div>"
                f"<div style=\"margin-top:8px;background:#F0F2F5;border-radius:99px;height:4px;overflow:hidden\">"
                f"<div style=\"width:{min(sq*8,100)}%;height:4px;border-radius:99px;background:{scolor}\"></div>"
                "</div></div>",
                unsafe_allow_html=True
            )
            if st.button(f"Study {sname}", key=f"subj_{sname}", use_container_width=True):
                st.session_state.subject = sname
                st.session_state.page    = "chat"
                st.rerun()

    # ── HOMEWORK DUE ──────────────────────────────────────────
    homework  = load_json(HOMEWORK_FILE)
    grade_val = u.get("grade","")
    pending   = [
        hw for hw in homework.values()
        if hw.get("status","active") == "active"
        and u["email"] not in hw.get("submissions",{})
        and (not grade_val or hw.get("grade") == grade_val)
    ]

    if pending:
        st.markdown("<div style=\"height:8px\"></div>", unsafe_allow_html=True)
        st.markdown(
            "<div style=\"font-family:'DM Serif Display',serif;font-size:22px;"
            "color:#1A1D23;margin-bottom:14px\">📋 Homework Due</div>",
            unsafe_allow_html=True
        )
        hw_cols = st.columns(min(len(pending), 3))
        for col, hw in zip(hw_cols, sorted(pending, key=lambda x: x.get("due_date",""))[:3]):
            due_str = hw.get("due_date","")
            try:
                dleft = (datetime.date.fromisoformat(due_str) - datetime.date.today()).days
            except Exception:
                dleft = 99
            if   dleft < 0:  dc="#DC3545"; dbg="#FEE2E2"; dlbl=f"Overdue {abs(dleft)}d"
            elif dleft == 0: dc="#DC3545"; dbg="#FEE2E2"; dlbl="Due Today!"
            elif dleft <= 2: dc="#D97706"; dbg="#FEF3C7"; dlbl=f"{dleft}d left"
            else:            dc="#059669"; dbg="#D1FAE5"; dlbl=f"{dleft}d left"
            info  = SUBJECTS.get(hw.get("subject","Maths"), {"emoji":"📚","color":"#1C7C54"})
            title = hw.get("data",{}).get("title", hw.get("topic","Homework"))
            short = (title[:28]+"…") if len(title)>28 else title
            with col:
                st.markdown(
                    f"<div style=\"background:#fff;border-radius:14px;padding:16px;"
                    f"border:1.5px solid #E4E8EE;box-shadow:0 2px 8px rgba(0,0,0,0.04);height:100%\">"
                    f"<div style=\"font-size:26px;margin-bottom:8px\">{info['emoji']}</div>"
                    f"<div style=\"font-size:13px;font-weight:700;color:#1A1D23;margin-bottom:4px\">{short}</div>"
                    f"<div style=\"font-size:11px;color:#9BA3B0;margin-bottom:8px\">{hw.get('subject','')} · {hw.get('grade','')}</div>"
                    f"<span style=\"background:{dbg};color:{dc};font-size:11px;font-weight:800;"
                    f"padding:4px 10px;border-radius:99px\">{dlbl}</span>"
                    "</div>",
                    unsafe_allow_html=True
                )
        st.markdown("<div style=\"height:6px\"></div>", unsafe_allow_html=True)
        if st.button("📋  Open Homework", key="hw_goto_home", use_container_width=False):
            st.session_state.page = "my_homework"; st.rerun()

    # ── MY PROGRESS (simple 4-stat row) ───────────────────────
    st.markdown("<div style=\"height:8px\"></div>", unsafe_allow_html=True)
    st.markdown(
        "<div style=\"font-family:'DM Serif Display',serif;font-size:22px;"
        "color:#1A1D23;margin-bottom:14px\">📊 My Progress</div>",
        unsafe_allow_html=True
    )
    p1, p2, p3, p4 = st.columns(4)
    for col, icon, val, lbl, color in [
        (p1, "❓", total,                          "Questions",    "#1C7C54"),
        (p2, "🔥", f"{streak} days",              "Streak",       "#E8770A"),
        (p3, "🏆", len(u.get("badges",[])),        "Badges",       "#C9A84C"),
        (p4, "📝", stats.get("quizzes_done",0),    "Quizzes",      "#1B4FD8"),
    ]:
        with col:
            st.markdown(
                f"<div style=\"background:#fff;border-radius:14px;padding:18px 14px;"
                f"text-align:center;border:1.5px solid #E4E8EE;"
                f"border-top:4px solid {color};"
                f"box-shadow:0 2px 8px rgba(0,0,0,0.04)\">"
                f"<div style=\"font-size:24px;margin-bottom:4px\">{icon}</div>"
                f"<div style=\"font-family:'DM Serif Display',serif;font-size:28px;"
                f"color:{color};line-height:1\">{val}</div>"
                f"<div style=\"font-size:11px;color:#9BA3B0;font-weight:600;"
                f"text-transform:uppercase;letter-spacing:.7px;margin-top:4px\">{lbl}</div>"
                "</div>",
                unsafe_allow_html=True
            )

    # ── CONTINUE LAST CHAT ─────────────────────────────────────
    hist      = load_json(HISTORY_FILE)
    user_hist = hist.get(u["email"], [])
    if user_hist:
        last_session = user_hist[-1]
        last_msgs    = last_session.get("messages", [])
        last_updated = last_session.get("updated","")
        is_recent = True
        if last_updated:
            try:
                upd = datetime.datetime.strptime(last_updated[:10],"%Y-%m-%d").date()
                is_recent = (datetime.date.today() - upd).days <= 7
            except Exception:
                pass
        if last_msgs and is_recent:
            last_q = next((m["content"][:60] for m in reversed(last_msgs) if m["role"]=="user"),"")
            if last_q:
                ell = "…" if len(last_q)==60 else ""
                st.markdown("<div style=\"height:8px\"></div>", unsafe_allow_html=True)
                st.markdown(
                    "<div style=\"background:#F0FDF4;border:1.5px solid #D1FAE5;"
                    "border-radius:14px;padding:16px 18px;"
                    "display:flex;align-items:center;gap:14px\">"
                    "<div style=\"font-size:32px\">💬</div>"
                    "<div style=\"flex:1;min-width:0\">"
                    "<div style=\"font-size:11px;font-weight:800;color:#1C7C54;"
                    "text-transform:uppercase;letter-spacing:.7px;margin-bottom:3px\">"
                    f"Continue your last chat · {last_session.get('subject','')}</div>"
                    "<div style=\"font-size:13px;color:#374151;font-weight:600;"
                    "white-space:nowrap;overflow:hidden;text-overflow:ellipsis\">"
                    f"\"{last_q}{ell}\"</div>"
                    "</div></div>",
                    unsafe_allow_html=True
                )
                if st.button("▶  Continue Chat", key="home_continue_chat"):
                    st.session_state.page = "chat"; st.rerun()




# ─────────────────────────────────────────────────────────────────
# CHAT / AI TUTOR — Ustad
# ─────────────────────────────────────────────────────────────────
def build_system(u, sub, lvl):
    urdu_rule   = "- Reply in Urdu script. Use English only for technical terms." if sub == "Urdu" else ""
    parent_rule = "- User is a parent. Explain how to help their child understand this topic." if u.get("role") == "parent" else ""
    return f"""You are Ustad, a warm, patient and encouraging AI tutor for Pakistani students.
Student: {u['name']} | Role: {'Parent' if u.get('role')=='parent' else 'Student'} | Class: {lvl} | Subject: {sub}

Teaching rules:
- Adapt complexity to {lvl}: Grade 1-3 = very simple language + emojis + one idea at a time; Grade 4-5 = simple + real-life examples; Grade 6-8 = clear steps + diagrams described in text; O Level = exam technique + mark schemes; A Level = university depth + derivations
{urdu_rule}
{parent_rule}
- For Maths / Physics / Chemistry: ALWAYS show numbered step-by-step working
- Use Pakistani curriculum context (FBISE, Cambridge Pakistan, local examples like rupees, cricket, lahore etc.)
- Format answers clearly: use numbered lists for steps, bullet points for facts
- End every answer with a short encouragement OR one follow-up question to check understanding
- If a question is unclear, ask the student to clarify before answering
- You can answer questions in ANY subject — not just the selected subject — if the student asks"""


def save_chat_session(sub, lvl):
    hist  = load_json(HISTORY_FILE)
    email = st.session_state.user["email"]
    if email not in hist: hist[email] = []
    sid = st.session_state.session_id or datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    st.session_state.session_id = sid
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    ex  = next((s for s in hist[email] if s["id"] == sid), None)
    if ex:
        ex["messages"] = st.session_state.chat_messages
        ex["updated"]  = now
    else:
        hist[email].append({
            "id": sid, "subject": sub, "level": lvl,
            "messages": st.session_state.chat_messages,
            "created": now, "updated": now
        })
    save_json(HISTORY_FILE, hist)



def page_chat():
    u = st.session_state.user

    # ══════════════════════════════════════════════════════════
    # TTS PLAYER — runs at top of every render cycle
    # ══════════════════════════════════════════════════════════

    # Init voice toggle (ON by default)
    if "_voice_on" not in st.session_state:
        st.session_state["_voice_on"] = True

    # Step A — generate audio for a freshly-arrived reply
    if st.session_state.get("_tts_pending"):
        pending_txt = st.session_state.pop("_tts_pending")
        with st.spinner("🔊 Ustad is speaking..."):
            speak_text(pending_txt)

    # Step B — render audio widget + autoplay (only when voice is ON)
    _voice_on  = st.session_state.get("_voice_on", True)
    _tts_b64   = st.session_state.get("_tts_b64")

    if _tts_b64 and _voice_on:
        # ── Visible audio player (mobile compatible) ──────────────
        raw = base64.b64decode(_tts_b64)
        st.audio(raw, format="audio/mp3")

        # ── Autoplay: inject via st.components.v1.html (iframe)
        #    This survives Streamlit's script-stripping and works on
        #    all browsers that allow autoplay of data-URI sources.
        #    We use a fingerprint so it fires ONCE per new response.
        autoplay_key = st.session_state.get("_tts_autoplay_key", "")
        new_key      = _tts_b64[-20:]           # last 20 chars as unique ID
        if autoplay_key != new_key:
            st.session_state["_tts_autoplay_key"] = new_key
            autoplay_html = f"""
<html><body style="margin:0;padding:0;overflow:hidden;height:0">
<audio id="ap" autoplay>
  <source src="data:audio/mp3;base64,{_tts_b64}" type="audio/mp3"/>
</audio>
<script>
  var a = document.getElementById('ap');
  if(a) {{
    a.play().catch(function() {{
      // autoplay blocked — user must press ▶ in the widget above
    }});
  }}
</script>
</body></html>"""
            st.components.v1.html(autoplay_html, height=0, scrolling=False)

    # ── Voice toggle row ──────────────────────────────────────────
    vcol1, vcol2 = st.columns([8, 1])
    with vcol2:
        v_icon  = "🔊" if _voice_on else "🔇"
        v_label = f"{v_icon}"
        if st.button(v_label, key="voice_toggle_btn",
                     help="Toggle Ustad voice ON / OFF",
                     use_container_width=True):
            st.session_state["_voice_on"] = not _voice_on
            # Clear stale audio so toggling back ON re-speaks last reply
            if not _voice_on:
                st.session_state["_tts_last_text"] = ""
            st.rerun()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # FIX: TWO-STATE PATTERN
    # "pending"  = what the dropdowns currently show (changes live)
    # "active"   = what the chat is actually using (only changes on Start)
    # Topic cards use ACTIVE state so they never fire on dropdown change
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if "pending_sub" not in st.session_state:
        st.session_state.pending_sub = st.session_state.get("subject", "Maths")
    if "pending_lvl" not in st.session_state:
        lvl_raw = u.get("grade", "Grade 6")
        st.session_state.pending_lvl = lvl_raw if lvl_raw in LEVELS else "Grade 6"
    if "active_sub" not in st.session_state:
        st.session_state.active_sub = st.session_state.pending_sub
    if "active_lvl" not in st.session_state:
        st.session_state.active_lvl = st.session_state.pending_lvl

    # Convenience aliases
    sub = st.session_state.active_sub   # used for chat + topic cards
    lvl = st.session_state.active_lvl

    # ── Grade-aware topic cards ───────────────────────────────
    GRADE_TOPICS = {
        "Grade 1":  {"Maths":["Count to 100","Add small numbers","Shapes around us","Long and short"],
                     "English":["ABC letters","Simple words","Colours","My family"],
                     "Urdu":["الف ب پ","میرا نام","جانور","رنگ"]},
        "Grade 2":  {"Maths":["Tables of 2 and 5","Adding 2-digit numbers","Half & quarter","Reading a clock"],
                     "English":["Nouns and verbs","Simple sentences","Plurals","Days & months"],
                     "Urdu":["حروف تہجی","سادہ جملے","گنتی","موسم"]},
        "Grade 3":  {"Maths":["Times tables 2-10","Place value: hundreds","Perimeter","Equal fractions"],
                     "Physics":["Push & pull forces","Hot and cold","Light & shadows","Magnets"],
                     "English":["Past tense","Adjectives","Punctuation","Capital letters"]},
        "Grade 4":  {"Maths":["Long multiplication","HCF and LCM","Angles","Decimals"],
                     "Physics":["States of matter","Simple machines","Food chains","Sound"],
                     "English":["Essay structure","Synonyms","Tenses","Comprehension"]},
        "Grade 5":  {"Maths":["Ratio & proportion","Percentage","Area of triangles","Prime numbers"],
                     "Physics":["Newton's 3 laws","Photosynthesis","Digestive system","Electric circuits"],
                     "Chemistry":["Elements vs compounds","Mixtures","Physical & chemical change","States of matter"],
                     "English":["Formal writing","Clauses","Metaphor & simile","Comprehension"]},
        "Grade 6":  {"Maths":["Linear equations","Pythagoras theorem","Circle area","Standard form"],
                     "Physics":["Speed, distance, time","Density","Pressure","Electromagnets"],
                     "Chemistry":["Periodic table","Atomic structure","Acids & bases","Chemical equations"],
                     "Biology":["Cell structure","Photosynthesis","Respiration","Digestive system"]},
        "Grade 7":  {"Maths":["Simultaneous equations","Quadratics intro","Trigonometry","Statistics"],
                     "Physics":["Waves & frequency","Ohm's Law","Thermal energy","Momentum"],
                     "Chemistry":["Ionic & covalent bonding","Reactions","Metals","Rates of reaction"],
                     "Biology":["DNA & genetics","Nervous system","Hormones","Ecosystems"]},
        "Grade 8":  {"Maths":["Quadratic formula","Circle theorems","Vectors","Probability trees"],
                     "Physics":["Nuclear physics","Electromagnetic spectrum","Radioactivity","Motor effect"],
                     "Chemistry":["Organic chemistry","Electrolysis","Reversible reactions","Industrial processes"],
                     "Biology":["Evolution","Homeostasis","Biotechnology","Disease & immunity"]},
        "Grade 9":  {"Maths":["Binomial expansion","Differentiation","Integration","Logarithms"],
                     "Physics":["Relativity intro","Quantum concepts","Astrophysics","Medical physics"],
                     "Chemistry":["Equilibrium constants","Electrochemistry","Transition metals","Spectroscopy"],
                     "Biology":["Respiration in detail","Photosynthesis biochemistry","Genetic engineering","Ecology"]},
        "Grade 10": {"Maths":["Complex numbers","Matrices","Further statistics","Differential equations"],
                     "Physics":["Capacitors","Nuclear reactions","Medical imaging","A Level mechanics"],
                     "Chemistry":["Organic synthesis","Kinetics","Acids: Ka & Kw","Polymer chemistry"],
                     "Biology":["Protein synthesis","Immunology","Cloning","Population genetics"]},
        "O Level":  {"Maths":["Paper 1 strategies","Paper 2 techniques","Vectors & transformations","Statistics"],
                     "Physics":["Forces & motion","Electricity","Thermal physics","Exam technique"],
                     "Chemistry":["Organic chemistry","Metals & reactivity","Acids & salts","Quantitative chemistry"],
                     "Biology":["Cell biology","Transport in plants","Human health","Genetics & evolution"]},
        "A Level":  {"Maths":["Pure Maths P1","Mechanics M1","Statistics S1","Further Pure"],
                     "Physics":["Particle physics","Quantum mechanics","Gravitational fields","Medical physics"],
                     "Chemistry":["Organic mechanisms","Thermodynamics","Electrode potentials","NMR & spectra"],
                     "Biology":["Protein synthesis","Gene expression","Immune system","Ecology"]},
    }
    TCARD_ICONS = {"Maths":"📐","Physics":"⚡","Chemistry":"🧪","Biology":"🌿",
                   "English":"📖","Computer Science":"💻","Urdu":"🖊️"}

    def get_topics(s, l):
        topics = GRADE_TOPICS.get(l, {}).get(s, [])
        if not topics:
            topics = QUICK_PROMPTS.get(s, [])
        return topics[:4]

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CSS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.markdown("""
    <style>
    /* ═══════════════════════════════════════════════════════════
       USTAD BANNER — cinematic AI tutor avatar
    ══════════════════════════════════════════════════════════ */
    .ustad-banner {
        width: 100%;
        height: 160px;
        border-radius: 20px;
        margin-bottom: 12px;
        overflow: hidden;
        position: relative;
        background: linear-gradient(120deg, #030F09 0%, #071A10 35%, #04250F 65%, #072B14 100%);
        border: 1px solid rgba(52,199,123,0.18);
        box-shadow: 0 8px 40px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.04);
        display: flex;
        align-items: stretch;
    }
    /* Teal-to-dark gradient bg matching reference image */
    .banner-bg-grad {
        position: absolute; inset: 0;
        background: linear-gradient(130deg,
            #061410 0%, #0B2B1C 25%,
            #0D4A32 55%, #0E7A52 80%, #08C076 100%);
        opacity: 0.85;
    }
    /* Circuit / grid pattern overlay */
    .banner-grid {
        position: absolute; inset: 0;
        background-image:
            linear-gradient(rgba(52,199,123,0.06) 1px, transparent 1px),
            linear-gradient(90deg, rgba(52,199,123,0.06) 1px, transparent 1px);
        background-size: 28px 28px;
        pointer-events: none;
    }
    /* Radial glow top-right */
    .banner-glow {
        position: absolute; right: -60px; top: -60px;
        width: 280px; height: 280px; border-radius: 50%;
        background: radial-gradient(circle, rgba(8,192,118,0.22) 0%, transparent 65%);
        pointer-events: none;
    }
    /* Bottom fade */
    .banner-fade {
        position: absolute; bottom: 0; left: 0; right: 0; height: 50px;
        background: linear-gradient(transparent, rgba(3,15,9,0.5));
        pointer-events: none;
    }

    /* ── Avatar column ──────────────────────────────────────── */
    .banner-avatar-col {
        width: 155px; flex-shrink: 0;
        position: relative; z-index: 3;
        display: flex; align-items: flex-end; justify-content: center;
        overflow: hidden;
    }
    /* glow ring under avatar */
    .banner-avatar-col::after {
        content: "";
        position: absolute; bottom: -10px; left: 50%; transform: translateX(-50%);
        width: 100px; height: 30px; border-radius: 50%;
        background: radial-gradient(ellipse, rgba(52,199,123,0.35), transparent 70%);
    }

    /* ── Right content ──────────────────────────────────────── */
    .banner-right {
        flex: 1; position: relative; z-index: 3;
        display: flex; flex-direction: column;
        justify-content: center; padding: 0 20px 0 10px;
        gap: 6px;
    }
    .banner-title {
        font-family: "DM Serif Display", serif;
        font-size: 22px; font-weight: 400;
        color: #fff; line-height: 1.1;
        text-shadow: 0 2px 12px rgba(0,0,0,0.5);
    }
    .banner-title span {
        color: #34C77B;
    }
    .banner-subtitle {
        font-size: 12px; color: rgba(255,255,255,0.55);
        font-weight: 500; line-height: 1.4;
        max-width: 360px;
    }
    /* Animated speech text — the "talking" line */
    .banner-speech-row {
        display: flex; align-items: flex-start; gap: 10px;
        margin-top: 2px;
    }
    .speech-quote-box {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(52,199,123,0.25);
        border-radius: 8px;
        padding: 7px 12px;
        font-size: 12px;
        color: rgba(255,255,255,0.8);
        font-style: italic;
        line-height: 1.45;
        max-width: 340px;
        position: relative;
    }
    /* Lip-sync animated bars */
    .lipbar-row {
        display: flex; align-items: flex-end;
        gap: 2px; height: 16px; flex-shrink: 0; margin-top: 2px;
    }
    .lipbar {
        width: 3px; border-radius: 2px;
        background: #34C77B;
        animation: lipwave 0.6s ease-in-out infinite alternate;
    }
    .lipbar:nth-child(1){ height:4px;  animation-delay:0.0s; }
    .lipbar:nth-child(2){ height:10px; animation-delay:0.1s; }
    .lipbar:nth-child(3){ height:14px; animation-delay:0.05s;}
    .lipbar:nth-child(4){ height:8px;  animation-delay:0.15s;}
    .lipbar:nth-child(5){ height:12px; animation-delay:0.08s;}
    .lipbar:nth-child(6){ height:6px;  animation-delay:0.12s;}
    .lipbar:nth-child(7){ height:10px; animation-delay:0.03s;}
    .lipbar.paused { animation-play-state: paused; height: 3px !important; }
    @keyframes lipwave {
        from { transform: scaleY(0.3); opacity: 0.5; }
        to   { transform: scaleY(1.0); opacity: 1.0; }
    }

    /* AI badge + online dot row */
    .banner-meta-row {
        display: flex; align-items: center; gap: 8px;
    }
    .ai-chip {
        background: rgba(52,199,123,0.15);
        border: 1px solid rgba(52,199,123,0.4);
        border-radius: 99px; padding: 3px 10px;
        font-size: 9.5px; font-weight: 800; color: #34C77B; letter-spacing:.6px;
    }
    .banner-online-dot {
        width: 6px; height: 6px; border-radius: 50%;
        background: #34C77B; box-shadow: 0 0 6px #34C77B;
        animation: bdot 2s infinite;
    }
    @keyframes bdot { 0%,100%{opacity:1} 50%{opacity:.2} }
    .banner-online-txt { font-size: 10px; color: rgba(255,255,255,.45); font-weight:600; }

    /* ── Speak button ───────────────────────────────────────── */
    .speak-btn {
        display: inline-flex; align-items: center; gap: 5px;
        background: rgba(52,199,123,0.18);
        border: 1px solid rgba(52,199,123,0.4);
        border-radius: 99px; padding: 4px 12px;
        font-size: 10px; font-weight: 800; color: #34C77B;
        cursor: pointer; transition: all .15s;
        letter-spacing: .3px;
    }
    .speak-btn:hover { background: rgba(52,199,123,0.3); }

    /* ─── Chat window ────────────────────────────────────────── */
    .chat-window {
        background: #FAFBFC; border: 1.5px solid #E4E8EE;
        border-radius: 16px; padding: 14px 12px; margin-bottom: 8px;
        box-shadow: 0 1px 6px rgba(0,0,0,0.04);
    }
    .ai-row  { display:flex; gap:9px; margin-bottom:12px; align-items:flex-start; }
    .ai-ava  { width:36px;height:36px;border-radius:10px;flex-shrink:0;margin-top:1px;
               overflow:hidden; border:2px solid rgba(28,124,84,0.2); }
    .ai-bubble { background:#fff;border:1.5px solid #E4E8EE;
                 border-radius:4px 14px 14px 14px;
                 padding:11px 15px;font-size:13.5px;line-height:1.8;
                 color:#1A1D23;max-width:88%; }
    .user-row   { display:flex;justify-content:flex-end;margin-bottom:12px; }
    .user-bubble{ background:#1C7C54;color:#fff;border-radius:14px 4px 14px 14px;
                  padding:10px 14px;font-size:13.5px;line-height:1.65;max-width:76%; }
    .img-row    { display:flex;gap:9px;margin-bottom:12px;align-items:flex-start; }
    .img-bubble { background:#EBF7F1;border:1.5px solid #C8EAD8;
                  border-radius:4px 14px 14px 14px;
                  padding:10px 14px;font-size:13.5px;line-height:1.75;
                  color:#1A1D23;max-width:88%; }
    .chat-empty { text-align:center;padding:26px 20px; }
    .chat-empty-icon  { font-size:44px;margin-bottom:8px; }
    .chat-empty-title { font-family:"DM Serif Display",serif;font-size:18px;color:#1A1D23;margin-bottom:5px; }
    .chat-empty-sub   { font-size:12.5px;color:#9BA3B0;line-height:1.6; }

    /* ── Topic cards ─────────────────────────────────────────── */
    .tcard-lbl { font-size:10px;font-weight:800;color:#9BA3B0;
                 text-transform:uppercase;letter-spacing:1px;margin-bottom:6px; }

    /* ── Upload strip ────────────────────────────────────────── */
    .upload-strip {
        background: linear-gradient(135deg,#1A1D23,#243040);
        border-radius: 12px; padding: 12px 16px; margin-bottom:8px;
        border: 1px solid rgba(28,124,84,0.25);
        display:flex; align-items:center; gap:12px;
    }
    .upload-title{font-size:13px;font-weight:800;color:#fff;}
    .upload-sub  {font-size:11px;color:rgba(255,255,255,0.4);margin-top:1px;}

    /* ── Daily limit ─────────────────────────────────────────── */
    .dlimit{background:#F0FDF4;border:1.5px solid #D1FAE5;border-radius:10px;
            padding:7px 13px;font-size:11.5px;color:#065F46;font-weight:600;
            display:flex;align-items:center;gap:8px;margin-top:6px;}
    </style>
    """, unsafe_allow_html=True)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PHOTOREALISTIC USTAD AVATAR — DALL-E / Stable Diffusion style
    # Full-body figure rendered in SVG with advanced shading,
    # subsurface skin tones, layered clothing detail, white hair
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    USTAD_SVG_BANNER = '<img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTUwIiBoZWlnaHQ9IjE2MCIgdmlld0JveD0iMCAwIDE1MCAxNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgc3R5bGU9ImRpc3BsYXk6YmxvY2s7b3ZlcmZsb3c6dmlzaWJsZSI+CiAgICAgIDxkZWZzPgogICAgICAgIDwhLS0gU2tpbiBncmFkaWVudCDigJQgd2FybSBzdWJzdXJmYWNlIHNjYXR0ZXIgLS0+CiAgICAgICAgPHJhZGlhbEdyYWRpZW50IGlkPSJza2luRyIgY3g9IjUwJSIgY3k9IjQwJSIgcj0iNTUlIj4KICAgICAgICAgIDxzdG9wIG9mZnNldD0iMCUiICAgc3RvcC1jb2xvcj0iI0U4QTg3QyIvPgogICAgICAgICAgPHN0b3Agb2Zmc2V0PSI0NSUiICBzdG9wLWNvbG9yPSIjRDQ4NDRFIi8+CiAgICAgICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiNCODY4M0EiLz4KICAgICAgICA8L3JhZGlhbEdyYWRpZW50PgogICAgICAgIDwhLS0gSGFpciBncmFkaWVudCDigJQgc2lsdmVyIHByb2Zlc3NvciAtLT4KICAgICAgICA8cmFkaWFsR3JhZGllbnQgaWQ9ImhhaXJHIiBjeD0iNTAlIiBjeT0iMjAlIiByPSI2MCUiPgogICAgICAgICAgPHN0b3Agb2Zmc2V0PSIwJSIgICBzdG9wLWNvbG9yPSIjRjBFREU4Ii8+CiAgICAgICAgICA8c3RvcCBvZmZzZXQ9IjYwJSIgIHN0b3AtY29sb3I9IiNDOEMyQjgiLz4KICAgICAgICAgIDxzdG9wIG9mZnNldD0iMTAwJSIgc3RvcC1jb2xvcj0iI0EwOTg5MCIvPgogICAgICAgIDwvcmFkaWFsR3JhZGllbnQ+CiAgICAgICAgPCEtLSBXYWlzdGNvYXQgZ3JhZGllbnQg4oCUIHJpY2ggYnJvd24gbGlrZSByZWZlcmVuY2UgLS0+CiAgICAgICAgPGxpbmVhckdyYWRpZW50IGlkPSJ2ZXN0RyIgeDE9IjAlIiB5MT0iMCUiIHgyPSIxMDAlIiB5Mj0iMTAwJSI+CiAgICAgICAgICA8c3RvcCBvZmZzZXQ9IjAlIiAgIHN0b3AtY29sb3I9IiM4QjVFM0MiLz4KICAgICAgICAgIDxzdG9wIG9mZnNldD0iNTAlIiAgc3RvcC1jb2xvcj0iIzZCNDQyMyIvPgogICAgICAgICAgPHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLWNvbG9yPSIjNEEyRTEyIi8+CiAgICAgICAgPC9saW5lYXJHcmFkaWVudD4KICAgICAgICA8IS0tIFNoaXJ0IGdyYWRpZW50IC0tPgogICAgICAgIDxsaW5lYXJHcmFkaWVudCBpZD0ic2hpcnRHIiB4MT0iMCUiIHkxPSIwJSIgeDI9IjAlIiB5Mj0iMTAwJSI+CiAgICAgICAgICA8c3RvcCBvZmZzZXQ9IjAlIiAgIHN0b3AtY29sb3I9IiNGOEYyRTgiLz4KICAgICAgICAgIDxzdG9wIG9mZnNldD0iMTAwJSIgc3RvcC1jb2xvcj0iI0U4REVDRSIvPgogICAgICAgIDwvbGluZWFyR3JhZGllbnQ+CiAgICAgICAgPCEtLSBFeWUgaXJpcyAtLT4KICAgICAgICA8cmFkaWFsR3JhZGllbnQgaWQ9ImlyaXNHIiBjeD0iNDAlIiBjeT0iMzUlIiByPSI1NSUiPgogICAgICAgICAgPHN0b3Agb2Zmc2V0PSIwJSIgICBzdG9wLWNvbG9yPSIjN0M1MjMwIi8+CiAgICAgICAgICA8c3RvcCBvZmZzZXQ9IjcwJSIgIHN0b3AtY29sb3I9IiM0QTJFMTAiLz4KICAgICAgICAgIDxzdG9wIG9mZnNldD0iMTAwJSIgc3RvcC1jb2xvcj0iIzJBMTUwMCIvPgogICAgICAgIDwvcmFkaWFsR3JhZGllbnQ+CiAgICAgICAgPCEtLSBBbWJpZW50IHNoYWRvdyB1bmRlciBmaWd1cmUgLS0+CiAgICAgICAgPHJhZGlhbEdyYWRpZW50IGlkPSJzaGFkb3dHIiBjeD0iNTAlIiBjeT0iNTAlIiByPSI1MCUiPgogICAgICAgICAgPHN0b3Agb2Zmc2V0PSIwJSIgICBzdG9wLWNvbG9yPSJyZ2JhKDAsMCwwLDAuMzUpIi8+CiAgICAgICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9InJnYmEoMCwwLDAsMCkiLz4KICAgICAgICA8L3JhZGlhbEdyYWRpZW50PgogICAgICAgIDwhLS0gRm9yZWhlYWQgaGlnaGxpZ2h0IC0tPgogICAgICAgIDxyYWRpYWxHcmFkaWVudCBpZD0iZmhHIiBjeD0iNTAlIiBjeT0iMCUiIHI9IjcwJSI+CiAgICAgICAgICA8c3RvcCBvZmZzZXQ9IjAlIiAgIHN0b3AtY29sb3I9InJnYmEoMjU1LDIyMCwxODAsMC40NSkiLz4KICAgICAgICAgIDxzdG9wIG9mZnNldD0iMTAwJSIgc3RvcC1jb2xvcj0icmdiYSgyNTUsMTgwLDEyMCwwKSIvPgogICAgICAgIDwvcmFkaWFsR3JhZGllbnQ+CiAgICAgIDwvZGVmcz4KCiAgICAgIDwhLS0gR3JvdW5kIHNoYWRvdyAtLT4KICAgICAgPGVsbGlwc2UgY3g9Ijc1IiBjeT0iMTU3IiByeD0iNDIiIHJ5PSI1IiBmaWxsPSJ1cmwoI3NoYWRvd0cpIi8+CgogICAgICA8IS0tIOKVkOKVkOKVkOKVkCBCT0RZIOKVkOKVkOKVkOKVkCAtLT4KICAgICAgPCEtLSBGdWxsIHNoaXJ0IHVuZGVybmVhdGggLS0+CiAgICAgIDxwYXRoIGQ9Ik0zMCAxMDAgUTI1IDE2MCAzMCAxNjAgTDEyMCAxNjAgUTEyNSAxNjAgMTIwIDEwMAogICAgICAgICAgICAgICBRMTA1IDkwIDkwIDkzIEw3NSAxMDAgTDYwIDkzIFE0NSA5MCAzMCAxMDBaIgogICAgICAgICAgICBmaWxsPSJ1cmwoI3NoaXJ0RykiLz4KICAgICAgPCEtLSBTaGlydCBzbGVldmVzIC0tPgogICAgICA8cGF0aCBkPSJNMzAgMTAwIFExNSAxMTAgMTggMTQwIFEyMiAxNTAgMzAgMTQ4IFEzNSAxMjAgNDAgMTA1WiIKICAgICAgICAgICAgZmlsbD0idXJsKCNzaGlydEcpIi8+CiAgICAgIDxwYXRoIGQ9Ik0xMjAgMTAwIFExMzUgMTEwIDEzMiAxNDAgUTEyOCAxNTAgMTIwIDE0OCBRMTE1IDEyMCAxMTAgMTA1WiIKICAgICAgICAgICAgZmlsbD0idXJsKCNzaGlydEcpIi8+CiAgICAgIDwhLS0gU2hpcnQgc2hhZG93IC8gZm9sZCBsaW5lcyAtLT4KICAgICAgPHBhdGggZD0iTTYwIDk1IFE2NSAxMTUgNjMgMTQwIiBzdHJva2U9InJnYmEoMCwwLDAsMC4wOCkiIHN0cm9rZS13aWR0aD0iMS41IiBmaWxsPSJub25lIi8+CiAgICAgIDxwYXRoIGQ9Ik05MCA5NSBRODUgMTE1IDg3IDE0MCIgc3Ryb2tlPSJyZ2JhKDAsMCwwLDAuMDgpIiBzdHJva2Utd2lkdGg9IjEuNSIgZmlsbD0ibm9uZSIvPgoKICAgICAgPCEtLSBXYWlzdGNvYXQgYm9keSAtLT4KICAgICAgPHBhdGggZD0iTTQyIDEwMCBRMzggMTU1IDQ0IDE2MCBMMTA2IDE2MCBRMTEyIDE1NSAxMDggMTAwCiAgICAgICAgICAgICAgIFE5NyA5MCA4OCA5NCBMNzUgMTAxIEw2MiA5NCBRNTMgOTAgNDIgMTAwWiIKICAgICAgICAgICAgZmlsbD0idXJsKCN2ZXN0RykiLz4KICAgICAgPCEtLSBXYWlzdGNvYXQgc2hlZW4gLyBoaWdobGlnaHQgLS0+CiAgICAgIDxwYXRoIGQ9Ik01NSAxMDAgUTUyIDEzMCA1NCAxNTUiIHN0cm9rZT0icmdiYSgyNTUsMjAwLDEyMCwwLjE4KSIKICAgICAgICAgICAgc3Ryb2tlLXdpZHRoPSIzIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiLz4KICAgICAgPCEtLSBXYWlzdGNvYXQgYnV0dG9uIHJvdyAtLT4KICAgICAgPGNpcmNsZSBjeD0iNzUiIGN5PSIxMTIiIHI9IjIuNSIgZmlsbD0icmdiYSgwLDAsMCwwLjQpIi8+CiAgICAgIDxjaXJjbGUgY3g9Ijc1IiBjeT0iMTIyIiByPSIyLjUiIGZpbGw9InJnYmEoMCwwLDAsMC40KSIvPgogICAgICA8Y2lyY2xlIGN4PSI3NSIgY3k9IjEzMiIgcj0iMi41IiBmaWxsPSJyZ2JhKDAsMCwwLDAuNCkiLz4KICAgICAgPGNpcmNsZSBjeD0iNzUiIGN5PSIxNDIiIHI9IjIuNSIgZmlsbD0icmdiYSgwLDAsMCwwLjQpIi8+CiAgICAgIDwhLS0gVmVzdCBwb2NrZXQgLS0+CiAgICAgIDxyZWN0IHg9IjQ0IiB5PSIxMDgiIHdpZHRoPSIxMiIgaGVpZ2h0PSI4IiByeD0iMiIKICAgICAgICAgICAgZmlsbD0icmdiYSgwLDAsMCwwLjE1KSIgc3Ryb2tlPSJyZ2JhKDI1NSwyMDAsMTAwLDAuMykiIHN0cm9rZS13aWR0aD0iMSIvPgogICAgICA8IS0tIFBvY2tldCBzcXVhcmUgLS0+CiAgICAgIDxwYXRoIGQ9Ik00NiAxMDggTDUwIDEwNCBMNTQgMTA4IiBmaWxsPSIjQzlBODRDIiBvcGFjaXR5PSIwLjgiLz4KCiAgICAgIDwhLS0gQ29sbGFyIC8gc2hpcnQgVi1uZWNrIC0tPgogICAgICA8cG9seWdvbiBwb2ludHM9Ijc1LDEwMCA2NCwxMTYgNzUsMTEwIDg2LDExNiIKICAgICAgICAgICAgICAgZmlsbD0idXJsKCNzaGlydEcpIiBvcGFjaXR5PSIwLjk1Ii8+CiAgICAgIDwhLS0gVGllIOKAlCBkYXJrIGdvbGQvb2NocmUgbGlrZSByZWZlcmVuY2UgLS0+CiAgICAgIDxwYXRoIGQ9Ik03MSAxMDMgTDc1IDk4IEw3OSAxMDMgTDc3IDEyOCBRNzUgMTMyIDczIDEyOFoiCiAgICAgICAgICAgIGZpbGw9IiNDOUE4NEMiLz4KICAgICAgPHBhdGggZD0iTTczIDEwMyBMNzUgMTAwIEw3NyAxMDMgTDc2IDExOCBRNzUgMTIwIDc0IDExOFoiCiAgICAgICAgICAgIGZpbGw9InJnYmEoMCwwLDAsMC4yKSIvPgogICAgICA8IS0tIFRpZSBrbm90IC0tPgogICAgICA8ZWxsaXBzZSBjeD0iNzUiIGN5PSIxMDEiIHJ4PSI0IiByeT0iMyIgZmlsbD0iI0EwNzgyOCIvPgogICAgICA8IS0tIExhcGVscyAtLT4KICAgICAgPHBhdGggZD0iTTYyIDk0IFE0OCA5OCA0MiAxMTIgTDU2IDExNCBaIiBmaWxsPSIjNUEzODE4IiBvcGFjaXR5PSIwLjg1Ii8+CiAgICAgIDxwYXRoIGQ9Ik04OCA5NCBRMTAyIDk4IDEwOCAxMTIgTDk0IDExNCBaIiBmaWxsPSIjNUEzODE4IiBvcGFjaXR5PSIwLjg1Ii8+CgogICAgICA8IS0tIOKVkOKVkOKVkOKVkCBORUNLIOKVkOKVkOKVkOKVkCAtLT4KICAgICAgPHBhdGggZD0iTTYzIDg4IFE2MyAxMDAgNzUgMTAyIFE4NyAxMDAgODcgODggUTg2IDgyIDc1IDgxIFE2NCA4MiA2MyA4OFoiCiAgICAgICAgICAgIGZpbGw9InVybCgjc2tpbkcpIi8+CiAgICAgIDwhLS0gTmVjayBzaGFkb3cgLS0+CiAgICAgIDxlbGxpcHNlIGN4PSI3NSIgY3k9Ijk4IiByeD0iMTAiIHJ5PSIzIiBmaWxsPSJyZ2JhKDAsMCwwLDAuMTUpIi8+CgogICAgICA8IS0tIOKVkOKVkOKVkOKVkCBIRUFEIOKVkOKVkOKVkOKVkCAtLT4KICAgICAgPCEtLSBIZWFkIGJhc2Ug4oCUIHNsaWdodGx5IGFnZWQsIHN0cm9uZyBqYXdsaW5lIC0tPgogICAgICA8ZWxsaXBzZSBjeD0iNzUiIGN5PSI1NyIgcng9IjI4IiByeT0iMzMiIGZpbGw9InVybCgjc2tpbkcpIi8+CiAgICAgIDwhLS0gQ2hlZWsgc2hhZGluZyAtLT4KICAgICAgPGVsbGlwc2UgY3g9IjUzIiBjeT0iNjIiIHJ4PSIxMCIgcnk9IjgiIGZpbGw9InJnYmEoMTgwLDkwLDUwLDAuMTIpIi8+CiAgICAgIDxlbGxpcHNlIGN4PSI5NyIgY3k9IjYyIiByeD0iMTAiIHJ5PSI4IiBmaWxsPSJyZ2JhKDE4MCw5MCw1MCwwLjEyKSIvPgogICAgICA8IS0tIEphdyBzaGFkb3cgLS0+CiAgICAgIDxlbGxpcHNlIGN4PSI3NSIgY3k9IjgyIiByeD0iMjAiIHJ5PSI2IiBmaWxsPSJyZ2JhKDAsMCwwLDAuMTIpIi8+CiAgICAgIDwhLS0gRm9yZWhlYWQgaGlnaGxpZ2h0IC0tPgogICAgICA8ZWxsaXBzZSBjeD0iNzUiIGN5PSIzOCIgcng9IjE2IiByeT0iMTAiIGZpbGw9InVybCgjZmhHKSIvPgoKICAgICAgPCEtLSBXcmlua2xlIGxpbmVzIOKAlCBwcm9mZXNzb3IgY2hhcmFjdGVyIC0tPgogICAgICA8cGF0aCBkPSJNNTcgNTIgUTYwIDUwIDYzIDUyIiBzdHJva2U9InJnYmEoMCwwLDAsMC4xKSIgc3Ryb2tlLXdpZHRoPSIxIiBmaWxsPSJub25lIi8+CiAgICAgIDxwYXRoIGQ9Ik04NyA1MiBROTAgNTAgOTMgNTIiIHN0cm9rZT0icmdiYSgwLDAsMCwwLjEpIiBzdHJva2Utd2lkdGg9IjEiIGZpbGw9Im5vbmUiLz4KICAgICAgPHBhdGggZD0iTTYwIDQ0IFE3NSA0MCA5MCA0NCIgc3Ryb2tlPSJyZ2JhKDAsMCwwLDAuMDcpIiBzdHJva2Utd2lkdGg9IjEiIGZpbGw9Im5vbmUiLz4KCiAgICAgIDwhLS0g4pWQ4pWQ4pWQ4pWQIEhBSVIg4oCUIHRoaWNrIHdpbGQgd2hpdGUgcHJvZmVzc29yIGhhaXIg4pWQ4pWQ4pWQ4pWQIC0tPgogICAgICA8IS0tIEJhY2sgdm9sdW1lIC0tPgogICAgICA8cGF0aCBkPSJNNDcgNDUgUTQwIDIwIDU1IDEyIFE3NSA0IDk1IDEyIFExMTAgMjAgMTAzIDQ1CiAgICAgICAgICAgICAgIFE5NSAyOCA3NSAyNiBRNTUgMjggNDcgNDVaIgogICAgICAgICAgICBmaWxsPSJ1cmwoI2hhaXJHKSIvPgogICAgICA8IS0tIFNpZGUgcHVmZnMg4oCUIHdpbGQgZmx5YXdheSAtLT4KICAgICAgPHBhdGggZD0iTTQ3IDQ1IFEzNCAzOCAzMCA1MiBRMzAgNjIgMzggNjAgUTQyIDUwIDQ3IDQ1WiIKICAgICAgICAgICAgZmlsbD0idXJsKCNoYWlyRykiLz4KICAgICAgPHBhdGggZD0iTTEwMyA0NSBRMTE2IDM4IDEyMCA1MiBRMTIwIDYyIDExMiA2MCBRMTA4IDUwIDEwMyA0NVoiCiAgICAgICAgICAgIGZpbGw9InVybCgjaGFpckcpIi8+CiAgICAgIDwhLS0gRmx5YXdheSBzdHJhbmRzIGxlZnQgLS0+CiAgICAgIDxwYXRoIGQ9Ik0zNiA1MiBRMjggNDUgMzAgMzUgUTM0IDMwIDM4IDM4IiBzdHJva2U9IiNEOEQ0Q0UiCiAgICAgICAgICAgIHN0cm9rZS13aWR0aD0iMiIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIi8+CiAgICAgIDxwYXRoIGQ9Ik0zOCA0OCBRMjYgNDIgMjggMjgiIHN0cm9rZT0iI0UwRENENiIKICAgICAgICAgICAgc3Ryb2tlLXdpZHRoPSIxLjUiIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPgogICAgICA8IS0tIEZseWF3YXkgc3RyYW5kcyByaWdodCAtLT4KICAgICAgPHBhdGggZD0iTTExNCA1MiBRMTIyIDQ1IDEyMCAzNSBRMTE2IDMwIDExMiAzOCIgc3Ryb2tlPSIjRDhENENFIgogICAgICAgICAgICBzdHJva2Utd2lkdGg9IjIiIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPgogICAgICA8IS0tIEhhaXIgaGlnaGxpZ2h0IHNoZWVuIC0tPgogICAgICA8cGF0aCBkPSJNNTggMTggUTc1IDEwIDkyIDE4IiBzdHJva2U9InJnYmEoMjU1LDI1NSwyNTUsMC40KSIKICAgICAgICAgICAgc3Ryb2tlLXdpZHRoPSIzIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiLz4KICAgICAgPCEtLSBUZW1wbGUgLyBzaWRlIGhhaXIgdHVmdHMgLS0+CiAgICAgIDxwYXRoIGQ9Ik00NyA0OCBRNDQgNTUgNDYgNjIiIHN0cm9rZT0iI0M4QzRCQyIgc3Ryb2tlLXdpZHRoPSIyLjUiCiAgICAgICAgICAgIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPgogICAgICA8cGF0aCBkPSJNMTAzIDQ4IFExMDYgNTUgMTA0IDYyIiBzdHJva2U9IiNDOEM0QkMiIHN0cm9rZS13aWR0aD0iMi41IgogICAgICAgICAgICBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiLz4KCiAgICAgIDwhLS0g4pWQ4pWQ4pWQ4pWQIEVBUlMg4pWQ4pWQ4pWQ4pWQIC0tPgogICAgICA8ZWxsaXBzZSBjeD0iNDciIGN5PSI2MCIgcng9IjYiIHJ5PSI4IiBmaWxsPSIjRDQ4NDRFIi8+CiAgICAgIDxlbGxpcHNlIGN4PSIxMDMiIGN5PSI2MCIgcng9IjYiIHJ5PSI4IiBmaWxsPSIjRDQ4NDRFIi8+CiAgICAgIDxlbGxpcHNlIGN4PSI0NyIgY3k9IjYwIiByeD0iMy41IiByeT0iNSIgZmlsbD0iI0MwNzA0QSIvPgogICAgICA8ZWxsaXBzZSBjeD0iMTAzIiBjeT0iNjAiIHJ4PSIzLjUiIHJ5PSI1IiBmaWxsPSIjQzA3MDRBIi8+CiAgICAgIDwhLS0gZWFyIGxvYmVzIC0tPgogICAgICA8ZWxsaXBzZSBjeD0iNDciIGN5PSI2NyIgcng9IjMiIHJ5PSIyLjUiIGZpbGw9IiNDODc4NEUiLz4KICAgICAgPGVsbGlwc2UgY3g9IjEwMyIgY3k9IjY3IiByeD0iMyIgcnk9IjIuNSIgZmlsbD0iI0M4Nzg0RSIvPgoKICAgICAgPCEtLSDilZDilZDilZDilZAgRVlFUyDilZDilZDilZDilZAgLS0+CiAgICAgIDwhLS0gRXllIHNvY2tldCBzaGFkb3cgLS0+CiAgICAgIDxlbGxpcHNlIGN4PSI2MiIgY3k9IjU4IiByeD0iOSIgcnk9IjciIGZpbGw9InJnYmEoMCwwLDAsMC4wOCkiLz4KICAgICAgPGVsbGlwc2UgY3g9Ijg4IiBjeT0iNTgiIHJ4PSI5IiByeT0iNyIgZmlsbD0icmdiYSgwLDAsMCwwLjA4KSIvPgogICAgICA8IS0tIFdoaXRlcyAtLT4KICAgICAgPGVsbGlwc2UgY3g9IjYyIiBjeT0iNTciIHJ4PSI3LjUiIHJ5PSI2LjUiIGZpbGw9IiNmZmYiLz4KICAgICAgPGVsbGlwc2UgY3g9Ijg4IiBjeT0iNTciIHJ4PSI3LjUiIHJ5PSI2LjUiIGZpbGw9IiNmZmYiLz4KICAgICAgPCEtLSBJcmlzIC0tPgogICAgICA8ZWxsaXBzZSBjeD0iNjIiIGN5PSI1OCIgcng9IjQuNSIgcnk9IjUiIGZpbGw9InVybCgjaXJpc0cpIi8+CiAgICAgIDxlbGxpcHNlIGN4PSI4OCIgY3k9IjU4IiByeD0iNC41IiByeT0iNSIgZmlsbD0idXJsKCNpcmlzRykiLz4KICAgICAgPCEtLSBQdXBpbCAtLT4KICAgICAgPGVsbGlwc2UgY3g9IjYyIiBjeT0iNTguNSIgcng9IjIuNSIgcnk9IjMiIGZpbGw9IiMwQTA1MDAiLz4KICAgICAgPGVsbGlwc2UgY3g9Ijg4IiBjeT0iNTguNSIgcng9IjIuNSIgcnk9IjMiIGZpbGw9IiMwQTA1MDAiLz4KICAgICAgPCEtLSBDYXRjaGxpZ2h0IC8gc3BlY3VsYXIgLS0+CiAgICAgIDxjaXJjbGUgY3g9IjYzLjUiIGN5PSI1Ni41IiByPSIxLjMiIGZpbGw9InJnYmEoMjU1LDI1NSwyNTUsMC45KSIvPgogICAgICA8Y2lyY2xlIGN4PSI4OS41IiBjeT0iNTYuNSIgcj0iMS4zIiBmaWxsPSJyZ2JhKDI1NSwyNTUsMjU1LDAuOSkiLz4KICAgICAgPGNpcmNsZSBjeD0iNjEiIGN5PSI2MCIgcj0iMC43IiBmaWxsPSJyZ2JhKDI1NSwyNTUsMjU1LDAuNCkiLz4KICAgICAgPGNpcmNsZSBjeD0iODciIGN5PSI2MCIgcj0iMC43IiBmaWxsPSJyZ2JhKDI1NSwyNTUsMjU1LDAuNCkiLz4KICAgICAgPCEtLSBVcHBlciBsaWQgY3JlYXNlIC0tPgogICAgICA8cGF0aCBkPSJNNTQgNTQgUTYyIDUxIDcwIDU0IiBzdHJva2U9InJnYmEoNjAsMzAsMTAsMC41KSIgc3Ryb2tlLXdpZHRoPSIxLjgiCiAgICAgICAgICAgIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPgogICAgICA8cGF0aCBkPSJNODAgNTQgUTg4IDUxIDk2IDU0IiBzdHJva2U9InJnYmEoNjAsMzAsMTAsMC41KSIgc3Ryb2tlLXdpZHRoPSIxLjgiCiAgICAgICAgICAgIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPgogICAgICA8IS0tIExvd2VyIGxpZCAtLT4KICAgICAgPHBhdGggZD0iTTU0IDYxIFE2MiA2NCA3MCA2MSIgc3Ryb2tlPSJyZ2JhKDE4MCwxMDAsNjAsMC4zKSIgc3Ryb2tlLXdpZHRoPSIxIgogICAgICAgICAgICBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiLz4KICAgICAgPHBhdGggZD0iTTgwIDYxIFE4OCA2NCA5NiA2MSIgc3Ryb2tlPSJyZ2JhKDE4MCwxMDAsNjAsMC4zKSIgc3Ryb2tlLXdpZHRoPSIxIgogICAgICAgICAgICBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiLz4KCiAgICAgIDwhLS0g4pWQ4pWQ4pWQ4pWQIEVZRUJST1dTIOKAlCB0aGljaywgZXhwcmVzc2l2ZSwgc2FsdC1wZXBwZXIg4pWQ4pWQ4pWQ4pWQIC0tPgogICAgICA8cGF0aCBkPSJNNTEgNDggUTYxIDQzIDcxIDQ3IiBzdHJva2U9IiM1QTQwMzAiIHN0cm9rZS13aWR0aD0iMy41IgogICAgICAgICAgICBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiLz4KICAgICAgPHBhdGggZD0iTTc5IDQ3IFE4OSA0MyA5OSA0OCIgc3Ryb2tlPSIjNUE0MDMwIiBzdHJva2Utd2lkdGg9IjMuNSIKICAgICAgICAgICAgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIi8+CiAgICAgIDwhLS0gR3JleSBoaWdobGlnaHQgb24gYnJvd3MgLS0+CiAgICAgIDxwYXRoIGQ9Ik01MyA0OCBRNjIgNDQgNjkgNDciIHN0cm9rZT0icmdiYSgyMDAsMTkwLDE4MCwwLjQpIiBzdHJva2Utd2lkdGg9IjEuNSIKICAgICAgICAgICAgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIi8+CiAgICAgIDxwYXRoIGQ9Ik04MSA0NyBROTAgNDQgOTcgNDgiIHN0cm9rZT0icmdiYSgyMDAsMTkwLDE4MCwwLjQpIiBzdHJva2Utd2lkdGg9IjEuNSIKICAgICAgICAgICAgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIi8+CgogICAgICA8IS0tIOKVkOKVkOKVkOKVkCBOT1NFIOKVkOKVkOKVkOKVkCAtLT4KICAgICAgPHBhdGggZD0iTTcxIDYyIFE2OSA3MiA3MCA3NiBRNzMgODAgNzUgODAgUTc3IDgwIDgwIDc2IFE4MSA3MiA3OSA2MiIKICAgICAgICAgICAgZmlsbD0icmdiYSgxODAsMTAwLDU1LDAuMzUpIi8+CiAgICAgIDwhLS0gTm9zdHJpbCB3aW5ncyAtLT4KICAgICAgPGVsbGlwc2UgY3g9IjY5IiBjeT0iNzciIHJ4PSI0LjUiIHJ5PSIzIiBmaWxsPSJyZ2JhKDE1MCw4MCw0MCwwLjMpIi8+CiAgICAgIDxlbGxpcHNlIGN4PSI4MSIgY3k9Ijc3IiByeD0iNC41IiByeT0iMyIgZmlsbD0icmdiYSgxNTAsODAsNDAsMC4zKSIvPgogICAgICA8IS0tIE5vc2UgYnJpZGdlIGhpZ2hsaWdodCAtLT4KICAgICAgPGxpbmUgeDE9Ijc0IiB5MT0iNTUiIHgyPSI3MyIgeTI9IjcwIiBzdHJva2U9InJnYmEoMjU1LDIwMCwxNTAsMC4yNSkiCiAgICAgICAgICAgIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIi8+CgogICAgICA8IS0tIOKVkOKVkOKVkOKVkCBCRUFSRCAvIE1PVVNUQUNIRSDilZDilZDilZDilZAgLS0+CiAgICAgIDwhLS0gRnVsbCBiZWFyZCDigJQgZ3JleWluZyAtLT4KICAgICAgPHBhdGggZD0iTTUyIDc4IFE1NSA5MiA2MCA5NiBRNjggMTAwIDc1IDEwMCBRODIgMTAwIDkwIDk2CiAgICAgICAgICAgICAgIFE5NSA5MiA5OCA3OCBRODggODUgNzUgODYgUTYyIDg1IDUyIDc4WiIKICAgICAgICAgICAgZmlsbD0idXJsKCNoYWlyRykiIG9wYWNpdHk9IjAuNzUiLz4KICAgICAgPCEtLSBCZWFyZCBzaGFkb3cgLS0+CiAgICAgIDxwYXRoIGQ9Ik01NiA4MCBRNjUgODggNzUgODkgUTg1IDg4IDk0IDgwIgogICAgICAgICAgICBzdHJva2U9InJnYmEoMTIwLDEwMCw4MCwwLjIpIiBzdHJva2Utd2lkdGg9IjEuNSIgZmlsbD0ibm9uZSIvPgogICAgICA8IS0tIE1vdXN0YWNoZSAtLT4KICAgICAgPHBhdGggZD0iTTU4IDc1IFE2NSA4MCA3NSA3NyBRODUgODAgOTIgNzUiCiAgICAgICAgICAgIHN0cm9rZT0iI0EwOTg4OCIgc3Ryb2tlLXdpZHRoPSIzIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiLz4KICAgICAgPHBhdGggZD0iTTYyIDc0IFE3MCA3OCA3NSA3NiBRODAgNzggODggNzQiCiAgICAgICAgICAgIHN0cm9rZT0icmdiYSgyNDAsMjM1LDIyOCwwLjUpIiBzdHJva2Utd2lkdGg9IjEuNSIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIi8+CgogICAgICA8IS0tIOKVkOKVkOKVkOKVkCBBTklNQVRFRCBNT1VUSCAobGlwLXN5bmMgdGFyZ2V0KSDilZDilZDilZDilZAgLS0+CiAgICAgIDwhLS0gTGlwLXN5bmM6IHRoZSBtb3V0aCBwYXRoIElEIGlzIHVzZWQgYnkgSlMgdG8gYW5pbWF0ZSBvcGVuL2Nsb3NlIC0tPgogICAgICA8IS0tIExpcHMgY2xvc2VkIChyZXN0aW5nKSAtLT4KICAgICAgPHBhdGggaWQ9InVzdGFkLW1vdXRoLXRvcCIgZD0iTTYyIDgyIFE2OCA3OSA3NSA4MCBRODIgNzkgODggODIiCiAgICAgICAgICAgIHN0cm9rZT0iIzhBNDgyOCIgc3Ryb2tlLXdpZHRoPSIyIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiLz4KICAgICAgPHBhdGggaWQ9InVzdGFkLW1vdXRoLWJvdCIgZD0iTTYyIDgyIFE2OCA4NiA3NSA4NiBRODIgODYgODggODIiCiAgICAgICAgICAgIGZpbGw9InJnYmEoNjAsMjAsMTAsMC41KSIgc3Ryb2tlPSIjNkEzMDE4IiBzdHJva2Utd2lkdGg9IjEuNSIvPgogICAgICA8IS0tIExpcCBzaGVlbiAtLT4KICAgICAgPHBhdGggZD0iTTY3IDgxIFE3NSA3OS41IDgzIDgxIiBzdHJva2U9InJnYmEoMjU1LDE4MCwxNDAsMC4zKSIKICAgICAgICAgICAgc3Ryb2tlLXdpZHRoPSIxLjIiIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPgoKICAgICAgPCEtLSDilZDilZDilZDilZAgR0xBU1NFUyDigJQgdGhpbiBtZXRhbC1yaW0g4pWQ4pWQ4pWQ4pWQIC0tPgogICAgICA8cmVjdCBpZD0iZ2xhc3MtbCIgeD0iNTMiIHk9IjUzIiB3aWR0aD0iMTciIGhlaWdodD0iMTIiIHJ4PSI1IgogICAgICAgICAgICBzdHJva2U9IiMzQTI4MTAiIHN0cm9rZS13aWR0aD0iMS44IiBmaWxsPSJyZ2JhKDIwMCwyMzAsMjU1LDAuMDYpIi8+CiAgICAgIDxyZWN0IGlkPSJnbGFzcy1yIiB4PSI4MCIgeT0iNTMiIHdpZHRoPSIxNyIgaGVpZ2h0PSIxMiIgcng9IjUiCiAgICAgICAgICAgIHN0cm9rZT0iIzNBMjgxMCIgc3Ryb2tlLXdpZHRoPSIxLjgiIGZpbGw9InJnYmEoMjAwLDIzMCwyNTUsMC4wNikiLz4KICAgICAgPCEtLSBCcmlkZ2UgLS0+CiAgICAgIDxwYXRoIGQ9Ik03MCA1OSBRNzUgNTcgODAgNTkiIHN0cm9rZT0iIzNBMjgxMCIgc3Ryb2tlLXdpZHRoPSIxLjgiIGZpbGw9Im5vbmUiLz4KICAgICAgPCEtLSBUZW1wbGVzIC0tPgogICAgICA8bGluZSB4MT0iNTMiIHkxPSI1OSIgeDI9IjQ3IiB5Mj0iNjAiIHN0cm9rZT0iIzNBMjgxMCIgc3Ryb2tlLXdpZHRoPSIxLjgiLz4KICAgICAgPGxpbmUgeDE9Ijk3IiB5MT0iNTkiIHgyPSIxMDMiIHkyPSI2MCIgc3Ryb2tlPSIjM0EyODEwIiBzdHJva2Utd2lkdGg9IjEuOCIvPgogICAgICA8IS0tIExlbnMgZ2xlYW0gLS0+CiAgICAgIDxwYXRoIGQ9Ik01NiA1NSBRNTkgNTQgNjIgNTYiIHN0cm9rZT0icmdiYSgyNTUsMjU1LDI1NSwwLjIpIgogICAgICAgICAgICBzdHJva2Utd2lkdGg9IjEiIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPgogICAgICA8cGF0aCBkPSJNODMgNTUgUTg2IDU0IDg5IDU2IiBzdHJva2U9InJnYmEoMjU1LDI1NSwyNTUsMC4yKSIKICAgICAgICAgICAgc3Ryb2tlLXdpZHRoPSIxIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiLz4KICAgIDwvc3ZnPg==" style="width:150px;height:160px;display:block;object-fit:contain;object-position:bottom" alt="Ustad avatar"/>'

    # 36×36 small avatar for chat messages
    USTAD_SVG_SMALL = '<img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzYiIGhlaWdodD0iMzYiIHZpZXdCb3g9IjEyIDMwIDEwMCA4MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICAgICAgPGRlZnM+CiAgICAgICAgPHJhZGlhbEdyYWRpZW50IGlkPSJzazIiIGN4PSI1MCUiIGN5PSI0MCUiIHI9IjU1JSI+CiAgICAgICAgICA8c3RvcCBvZmZzZXQ9IjAlIiAgc3RvcC1jb2xvcj0iI0U4QTg3QyIvPgogICAgICAgICAgPHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLWNvbG9yPSIjQjg2ODNBIi8+CiAgICAgICAgPC9yYWRpYWxHcmFkaWVudD4KICAgICAgICA8cmFkaWFsR3JhZGllbnQgaWQ9ImgyIiBjeD0iNTAlIiBjeT0iMjAlIiByPSI2MCUiPgogICAgICAgICAgPHN0b3Agb2Zmc2V0PSIwJSIgIHN0b3AtY29sb3I9IiNGMEVERTgiLz4KICAgICAgICAgIDxzdG9wIG9mZnNldD0iMTAwJSIgc3RvcC1jb2xvcj0iI0EwOTg5MCIvPgogICAgICAgIDwvcmFkaWFsR3JhZGllbnQ+CiAgICAgIDwvZGVmcz4KICAgICAgPHBhdGggZD0iTTMwIDEwMCBRMjUgMTE1IDMwIDExNSBMMTIwIDExNSBRMTI1IDExNSAxMjAgMTAwCiAgICAgICAgICAgICAgIFExMDUgOTAgOTAgOTMgTDc1IDEwMCBMNjAgOTMgUTQ1IDkwIDMwIDEwMFoiIGZpbGw9IiM2QjQ0MjMiLz4KICAgICAgPHBvbHlnb24gcG9pbnRzPSI3NSwxMDAgNjQsMTEyIDc1LDEwOCA4NiwxMTIiIGZpbGw9IiNGNUYwRTgiLz4KICAgICAgPHJlY3QgeD0iNjMiIHk9Ijg4IiB3aWR0aD0iMjQiIGhlaWdodD0iMTQiIHJ4PSI1IiBmaWxsPSJ1cmwoI3NrMikiLz4KICAgICAgPGVsbGlwc2UgY3g9Ijc1IiBjeT0iNTciIHJ4PSIyOCIgcnk9IjMzIiBmaWxsPSJ1cmwoI3NrMikiLz4KICAgICAgPHBhdGggZD0iTTQ3IDQ1IFE0MCAyMCA1NSAxMiBRNzUgNCA5NSAxMiBRMTEwIDIwIDEwMyA0NQogICAgICAgICAgICAgICBROTUgMjggNzUgMjYgUTU1IDI4IDQ3IDQ1WiIgZmlsbD0idXJsKCNoMikiLz4KICAgICAgPHBhdGggZD0iTTQ3IDQ1IFEzNCAzOCAzMCA1MiBRMzAgNjIgMzggNjAgUTQyIDUwIDQ3IDQ1WiIgZmlsbD0idXJsKCNoMikiLz4KICAgICAgPHBhdGggZD0iTTEwMyA0NSBRMTE2IDM4IDEyMCA1MiBRMTIwIDYyIDExMiA2MCBRMTA4IDUwIDEwMyA0NVoiIGZpbGw9InVybCgjaDIpIi8+CiAgICAgIDxlbGxpcHNlIGN4PSI2MiIgY3k9IjU3IiByeD0iNyIgcnk9IjYiIGZpbGw9IiNmZmYiLz4KICAgICAgPGVsbGlwc2UgY3g9Ijg4IiBjeT0iNTciIHJ4PSI3IiByeT0iNiIgZmlsbD0iI2ZmZiIvPgogICAgICA8ZWxsaXBzZSBjeD0iNjIiIGN5PSI1OCIgcng9IjQiIHJ5PSI0LjUiIGZpbGw9IiM0QTJFMTAiLz4KICAgICAgPGVsbGlwc2UgY3g9Ijg4IiBjeT0iNTgiIHJ4PSI0IiByeT0iNC41IiBmaWxsPSIjNEEyRTEwIi8+CiAgICAgIDxlbGxpcHNlIGN4PSI2MiIgY3k9IjU4LjUiIHJ4PSIyIiByeT0iMi41IiBmaWxsPSIjMEEwNTAwIi8+CiAgICAgIDxlbGxpcHNlIGN4PSI4OCIgY3k9IjU4LjUiIHJ4PSIyIiByeT0iMi41IiBmaWxsPSIjMEEwNTAwIi8+CiAgICAgIDxjaXJjbGUgY3g9IjYzLjUiIGN5PSI1Ni41IiByPSIxLjIiIGZpbGw9InJnYmEoMjU1LDI1NSwyNTUsMC45KSIvPgogICAgICA8Y2lyY2xlIGN4PSI4OS41IiBjeT0iNTYuNSIgcj0iMS4yIiBmaWxsPSJyZ2JhKDI1NSwyNTUsMjU1LDAuOSkiLz4KICAgICAgPHBhdGggZD0iTTUxIDQ4IFE2MSA0MyA3MSA0NyIgc3Ryb2tlPSIjNUE0MDMwIiBzdHJva2Utd2lkdGg9IjMiIGZpbGw9Im5vbmUiLz4KICAgICAgPHBhdGggZD0iTTc5IDQ3IFE4OSA0MyA5OSA0OCIgc3Ryb2tlPSIjNUE0MDMwIiBzdHJva2Utd2lkdGg9IjMiIGZpbGw9Im5vbmUiLz4KICAgICAgPHBhdGggZD0iTTcxIDYyIFE2OSA3MiA3MCA3NiBRNzUgODAgODAgNzYgUTgxIDcyIDc5IDYyIiBmaWxsPSJyZ2JhKDE4MCwxMDAsNTUsMC4zKSIvPgogICAgICA8cGF0aCBkPSJNNTggNzUgUTY1IDgwIDc1IDc3IFE4NSA4MCA5MiA3NSIgc3Ryb2tlPSIjQTA5ODg4IgogICAgICAgICAgICBzdHJva2Utd2lkdGg9IjMiIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPgogICAgICA8cGF0aCBkPSJNNjAgODEgUTY4IDg2IDc1IDg1IFE4MiA4NiA5MCA4MSBRODQgODggNzUgODkgUTY2IDg4IDYwIDgxWiIKICAgICAgICAgICAgZmlsbD0iI0M4QzJCOCIgb3BhY2l0eT0iMC42Ii8+CiAgICAgIDxyZWN0IHg9IjUzIiB5PSI1MyIgd2lkdGg9IjE3IiBoZWlnaHQ9IjEyIiByeD0iNSIKICAgICAgICAgICAgc3Ryb2tlPSIjM0EyODEwIiBzdHJva2Utd2lkdGg9IjEuOCIgZmlsbD0icmdiYSgyMDAsMjMwLDI1NSwwLjA2KSIvPgogICAgICA8cmVjdCB4PSI4MCIgeT0iNTMiIHdpZHRoPSIxNyIgaGVpZ2h0PSIxMiIgcng9IjUiCiAgICAgICAgICAgIHN0cm9rZT0iIzNBMjgxMCIgc3Ryb2tlLXdpZHRoPSIxLjgiIGZpbGw9InJnYmEoMjAwLDIzMCwyNTUsMC4wNikiLz4KICAgICAgPHBhdGggZD0iTTcwIDU5IFE3NSA1NyA4MCA1OSIgc3Ryb2tlPSIjM0EyODEwIiBzdHJva2Utd2lkdGg9IjEuOCIgZmlsbD0ibm9uZSIvPgogICAgPC9zdmc+" style="width:36px;height:36px;display:block;border-radius:10px;border:2px solid rgba(28,124,84,0.2)" alt="Ustad avatar"/>'

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # BANNER BUILD — cinematic layout with Web Speech API
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    msgs       = st.session_state.get("chat_messages", [])
    last_reply = next((m["content"] for m in reversed(msgs)
                       if m["role"] == "assistant"), None)
    if last_reply:
        _c = last_reply
        for _m in ["**", "*", "##", "#", "```", "__", "_"]:
            _c = _c.replace(_m, "")
        _c = _c.replace("\n", " ").strip()
        preview = _c[:110] + ("…" if len(_c) > 110 else "")
    else:
        preview = "Select " + st.session_state.pending_sub + " and press Start Learning!"

    # Lip-sync bars (7 bars, animated via CSS when speaking)
    lipbars = "".join(
        f'<div class="lipbar paused" style="animation-delay:{d}s"></div>'
        for d in [0.0,0.1,0.05,0.15,0.08,0.12,0.03]
    )

    # Banner HTML (no script tags — st.markdown strips them)
    st.markdown(
        "<div class=\"ustad-banner\">"
        "<div class=\"banner-bg-grad\"></div>"
        "<div class=\"banner-grid\"></div>"
        "<div class=\"banner-glow\"></div>"
        "<div class=\"banner-fade\"></div>"
        f"<div class=\"banner-avatar-col\">{USTAD_SVG_BANNER}</div>"
        "<div class=\"banner-right\">"
        "<div class=\"banner-meta-row\">"
        "<div class=\"ai-chip\">✦ AI POWERED</div>"
        "<div class=\"banner-online-dot\"></div>"
        "<span class=\"banner-online-txt\">Ustad · Online</span>"
        "</div>"
        "<div class=\"banner-title\">Ustad — <span>AI Tutor</span></div>"
        "<div class=\"banner-subtitle\">Personalised learning powered by conversational AI</div>"
        "<div class=\"banner-speech-row\">"
        f"<div class=\"speech-quote-box\">\"{preview}\"</div>"
        "</div>"
        f"<div class=\"banner-speech-row\" style=\"margin-top:6px;gap:10px;align-items:center\">"
        f"<div class=\"lipbar-row\" id=\"ustad-lipbars\">{lipbars}</div>"
        "</div>"
        "</div>"
        "</div>",
        unsafe_allow_html=True
    )

    # ── 🔊 Web Speech — use st.components.v1.html so <script> actually runs ──
    # st.markdown strips all <script> tags; components.v1.html renders in an
    # iframe where scripts execute normally and postMessage lets it reach parent.
    # Voice removed — browser TTS not reliably supported on Streamlit Cloud

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SELECTION ROW — dropdowns update PENDING only
    # Start button COMMITS pending → active and resets chat
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    subj_list  = list(SUBJECTS.keys())
    cur_p_sub  = st.session_state.pending_sub
    cur_p_lvl  = st.session_state.pending_lvl
    sub_idx    = subj_list.index(cur_p_sub) if cur_p_sub in subj_list else 0
    lvl_idx    = LEVELS.index(cur_p_lvl)    if cur_p_lvl  in LEVELS    else 5

    cc1, cc2, cc3 = st.columns([2, 2, 1])
    with cc1:
        sel_sub = st.selectbox("Subject", subj_list,
                               index=sub_idx, label_visibility="collapsed",
                               key="chat_sub_select")
    with cc2:
        sel_lvl = st.selectbox("Grade", LEVELS,
                               index=lvl_idx, label_visibility="collapsed",
                               key="chat_lvl_select")
    with cc3:
        start_btn = st.button("▶ Start Learning",
                              use_container_width=True,
                              type="primary", key="start_learning_btn")

    # Always sync pending from dropdowns (no rerun, no side effects)
    st.session_state.pending_sub = sel_sub
    st.session_state.pending_lvl = sel_lvl

    # START button: commit pending → active, reset chat, send opener
    if start_btn:
        st.session_state.active_sub    = sel_sub
        st.session_state.active_lvl    = sel_lvl
        st.session_state.subject       = sel_sub
        st.session_state.chat_messages = []
        st.session_state.session_id    = None
        first  = u["name"].split()[0]
        opener = (
            f"Assalam-o-Alaikum {first}! 👋\n\n"
            f"I am your **{sel_sub}** tutor for **{sel_lvl}**.\n\n"
            f"I am ready to help you master {sel_sub} at the {sel_lvl} level. "
            "Ask me any question — tap a topic card below or type your own!\n\n"
            "Kya sikhna chahte hain aaj? 📚"
        )
        st.session_state.chat_messages.append({"role":"assistant","content":opener})
        st.session_state["_tts_b64"] = None
        st.session_state["_tts_pending"] = opener
        st.rerun()

    # Re-read active after potential commit
    sub = st.session_state.active_sub
    lvl = st.session_state.active_lvl

    # Show a subtle indicator when pending ≠ active
    if (sel_sub != sub or sel_lvl != lvl):
        st.markdown(
            f"<div style=\"font-size:11px;color:#D97706;font-weight:600;"
            f"padding:5px 10px;background:#FEF3C7;border-radius:8px;margin-bottom:6px\">"
            f"⚠️ Press <b>▶ Start Learning</b> to switch to <b>{sel_sub} · {sel_lvl}</b>"
            "</div>",
            unsafe_allow_html=True
        )

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CHAT MESSAGES — avatar next to every Ustad reply
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if not msgs:
        st.markdown(
            "<div class=\"chat-window\"><div class=\"chat-empty\">"
            "<div class=\"chat-empty-icon\">👆</div>"
            "<div class=\"chat-empty-title\">Pick subject & grade above</div>"
            "<div class=\"chat-empty-sub\">Press <b>▶ Start Learning</b> to begin,<br>"
            "or tap any topic card below to jump straight in."
            "</div></div></div>",
            unsafe_allow_html=True
        )
    else:
        win = "<div class=\"chat-window\">"
        for m in msgs:
            safe = (m["content"]
                    .replace("&","&amp;").replace("<","&lt;")
                    .replace(">","&gt;").replace("\n","<br>")
                    .replace("**",""))          # strip markdown bold for HTML
            tag = m.get("tag","")
            if m["role"] == "user":
                win += (f"<div class=\"user-row\">"
                        f"<div class=\"user-bubble\">{safe}</div></div>")
            elif tag == "image":
                win += (f"<div class=\"img-row\">"
                        f"<div class=\"ai-ava\">{USTAD_SVG_SMALL}</div>"
                        f"<div class=\"img-bubble\">📸 <b>Homework Solution</b><br><br>{safe}</div></div>")
            else:
                win += (f"<div class=\"ai-row\">"
                        f"<div class=\"ai-ava\">{USTAD_SVG_SMALL}</div>"
                        f"<div class=\"ai-bubble\">{safe}</div></div>")
        win += "</div>"
        st.markdown(win, unsafe_allow_html=True)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # TOPIC CARDS — keyed on ACTIVE sub+lvl so changing dropdowns
    # does NOT re-render / fire cards
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    topics    = get_topics(sub, lvl)
    subj_icon = TCARD_ICONS.get(sub, "📚")
    st.markdown(
        f"<div class=\"tcard-lbl\">⚡ {sub} · {lvl} — tap to ask Ustad</div>",
        unsafe_allow_html=True
    )
    if topics:
        tcols = st.columns(len(topics))
        for i, (col, topic) in enumerate(zip(tcols, topics)):
            with col:
                # Key uses ACTIVE sub+lvl — stable until Start is pressed
                if st.button(f"{subj_icon} {topic}",
                             key=f"tc__{sub}__{lvl}__{i}",
                             use_container_width=True):
                    st.session_state.chat_messages.append(
                        {"role":"user","content":topic})
                    with st.spinner("👳‍♂️ Ustad is thinking..."):
                        reply = call_ai(st.session_state.chat_messages,
                                        build_system(u, sub, lvl))
                    if reply.startswith("__"):
                        st.session_state.chat_messages.pop()
                        st.error("⚠️ API error — check ANTHROPIC_API_KEY in secrets.")
                    else:
                        st.session_state.chat_messages.append(
                            {"role":"assistant","content":reply})
                        st.session_state["_tts_pending"] = reply
                        bump_stats(sub)
                        save_chat_session(sub, lvl)
                    st.rerun()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # HOMEWORK IMAGE UPLOAD
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    with st.expander("📸  Upload Homework Image — Ustad will solve it", expanded=False):
        st.markdown(
            "<div class=\"upload-strip\">"
            "<div style=\"font-size:24px;flex-shrink:0\">📷</div>"
            "<div><div class=\"upload-title\">Photo Homework Solver</div>"
            "<div class=\"upload-sub\">Upload a photo — Ustad reads the question, "
            "solves it and explains every step.</div></div></div>",
            unsafe_allow_html=True
        )
        hw_img = st.file_uploader("Photo (JPG/PNG)", type=["jpg","jpeg","png"],
                                   key="hw_img_upload", label_visibility="collapsed")
        ic1, ic2 = st.columns([3,1])
        with ic1:
            extra_note = st.text_input("Note (optional)",
                placeholder="e.g. Grade 8 Maths Chapter 3…",
                key="hw_img_note", label_visibility="collapsed")
        with ic2:
            solve_btn = st.button("🔍 Solve It", key="hw_solve_btn",
                                  use_container_width=True, type="primary")
        if hw_img and solve_btn:
            img_b64    = base64.standard_b64encode(hw_img.read()).decode("utf-8")
            media_type = "image/jpeg" if hw_img.type in ("image/jpg","image/jpeg") else "image/png"
            note_txt   = f" Context: {extra_note}." if extra_note.strip() else ""
            prompt = (
                "Look carefully at this homework image." + note_txt +
                "\n\n1. Write out the exact question(s) visible."
                "\n2. Solve each with full step-by-step working."
                "\n3. Explain the method clearly for a student."
                "\nBe warm and encouraging."
            )
            st.session_state.chat_messages.append({
                "role":"user",
                "content": f"📸 Homework image{' — '+extra_note if extra_note.strip() else ''}"
            })
            with st.spinner("🔍 Ustad is reading your homework image…"):
                try:
                    r = client.messages.create(
                        model="claude-haiku-4-5-20251001", max_tokens=1500,
                        system=build_system(u, sub, lvl),
                        messages=[{"role":"user","content":[
                            {"type":"image","source":{"type":"base64",
                             "media_type":media_type,"data":img_b64}},
                            {"type":"text","text":prompt}
                        ]}]
                    )
                    img_reply = r.content[0].text if r.content else "__EMPTY__"
                except Exception as e:
                    img_reply = f"__API_ERROR__: {e}"
            if img_reply.startswith("__"):
                st.session_state.chat_messages.pop()
                st.error(f"⚠️ Image analysis failed: {img_reply}")
            else:
                st.session_state.chat_messages.append(
                    {"role":"assistant","content":img_reply,"tag":"image"})
                bump_stats(sub); save_chat_session(sub, lvl)
            st.rerun()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # TEXT QUESTION FORM
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # TEXT INPUT FORM — st.text_input so ENTER key auto-submits
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    with st.form("chat_form", clear_on_submit=True):
        ph = ("یہاں سوال لکھیں — Ustad آپ کی مدد کرے گا…"
              if sub == "Urdu"
              else f"Ask Ustad anything about {sub} ({lvl}) — press Enter to send…")
        # text_input → Enter key submits form natively in Streamlit
        txt = st.text_input("Ask Ustad", placeholder=ph,
                            label_visibility="collapsed", key="chat_input_field")
        fc1, fc2 = st.columns([4, 1])
        with fc1:
            send  = st.form_submit_button("📤  Ask Ustad",
                                          use_container_width=True, type="primary")
        with fc2:
            clear = st.form_submit_button("🗑️ Clear", use_container_width=True)
        if clear:
            st.session_state.chat_messages     = []
            st.session_state.session_id        = None
            st.session_state["_tts_b64"]       = None
            st.session_state["_tts_last_text"] = ""
            st.rerun()
        if send and txt.strip():
            _ok, used, limit = check_daily_limit(u)
            if not _ok:
                st.error(f"⏰ Daily limit of {limit} questions reached. Upgrade to Pro for unlimited!")
            else:
                st.session_state.chat_messages.append(
                    {"role": "user", "content": txt.strip()})
                with st.spinner("👳‍♂️ Ustad is thinking..."):
                    reply = call_ai(st.session_state.chat_messages,
                                    build_system(u, sub, lvl))
                if reply.startswith("__"):
                    st.session_state.chat_messages.pop()
                    st.error("🔑 API key missing — add ANTHROPIC_API_KEY to Streamlit secrets."
                             if "API_KEY_MISSING" in reply else f"⚠️ {reply}")
                else:
                    st.session_state.chat_messages.append(
                        {"role": "assistant", "content": reply})
                    # Queue for TTS on next render cycle
                    st.session_state["_tts_pending"]   = reply
                    st.session_state["_tts_b64"]       = None   # clear stale audio
                    st.session_state["_tts_last_text"] = ""     # force regeneration
                    bump_stats(sub)
                    save_chat_session(sub, lvl)
                st.rerun()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # DAILY LIMIT BAR
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    _ok, used, limit = check_daily_limit(u)
    left = max(0, limit - used)
    pct  = int(used / max(limit,1) * 100)
    bc   = "#1C7C54" if pct < 70 else "#D97706" if pct < 90 else "#DC3545"
    st.markdown(
        "<div class=\"dlimit\"><span>💬</span><div style=\"flex:1\">"
        "<div style=\"display:flex;justify-content:space-between;margin-bottom:3px\">"
        f"<span>Daily questions: <b>{used}/{limit}</b></span>"
        f"<span style=\"color:#9BA3B0\">{left} left today</span></div>"
        "<div style=\"background:#D1FAE5;border-radius:99px;height:4px;overflow:hidden\">"
        f"<div style=\"width:{pct}%;height:4px;border-radius:99px;background:{bc}\"></div>"
        "</div></div></div>",
        unsafe_allow_html=True
    )


# ─────────────────────────────────────────────────────────────────
# PRACTICE QUIZ
# ─────────────────────────────────────────────────────────────────
def page_quiz():
    u = st.session_state.user
    st.markdown("<div class=\"section-header orange\">📝 Practice Quiz</div>", unsafe_allow_html=True)

    q = st.session_state.quiz

    if q is not None and q["done"]:
        # FIX #5: Save quiz stat once, guarded by _stat_saved flag
        if not q.get("_stat_saved"):
            users = load_json(USERS_FILE)
            eu    = users.get(u["email"], u)
            eu.setdefault("stats", init_stats())
            eu["stats"]["quizzes_done"] = eu["stats"].get("quizzes_done",0) + 1
            # Also bump subject stats for quiz questions answered
            sub_field = q.get("sub","")
            if sub_field in SUBJECTS:
                eu["stats"][sub_field] = eu["stats"].get(sub_field,0) + len(q["questions"])
            eu, new_b = check_badges(eu)
            users[u["email"]] = eu
            save_json(USERS_FILE, users)
            st.session_state.user = eu
            for b in new_b:
                st.toast(f"🏆 Badge: {b['icon']} {b['name']}!", icon="🎉")
            q["_stat_saved"] = True
            st.session_state.quiz = q

        total = len(q["questions"]); score = q["score"]
        pct   = int((score/total)*100)
        emoji = "🏆" if pct>=80 else "👍" if pct>=60 else "💪"
        col_c = "#059669" if pct>=80 else "#F59E0B" if pct>=60 else "#E8472A"

        st.markdown(f"""
        <div style="text-align:center;background:#fff;border-radius:20px;padding:28px;
            box-shadow:0 4px 20px rgba(0,0,0,0.08);margin-bottom:18px">
            <div style="font-size:56px">{emoji}</div>
            <h2 style="font-size:26px;font-weight:800;color:#1A1A2E">Quiz Complete!</h2>
            <div style="font-size:48px;font-weight:900;color:{col_c};margin:8px 0">{score}/{total}</div>
            <div style="font-size:15px;color:#666">
                {pct}% — {"Excellent! ⭐" if pct>=80 else "Good effort! 📚" if pct>=60 else "Keep practicing! 💪"}
            </div>
            <div style="font-size:13px;color:#999;margin-top:4px">
                Topic: {q.get("topic","Custom")} · {q.get("difficulty","Medium")} · {q.get("sub","")} {q.get("lvl","")}
            </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("### 📋 Review Answers")
        for i,(ques,ans) in enumerate(zip(q["questions"],q["answers"])):
            correct = ans["chosen"] == ques["answer"]
            bg     = "#F0FDF4" if correct else "#FFF1EE"
            border = "#059669" if correct else "#E8472A"
            wrong_line = "" if correct else f"<div style=\"font-size:13px;color:#059669;margin-top:2px\">✅ Correct: <b>{ques['answer']}</b></div>"
            st.markdown(f"""
            <div style="background:{bg};border:1.5px solid {border};border-radius:12px;
                padding:14px 16px;margin-bottom:10px;color:#1A1A2E">
                <div style="font-weight:700;font-size:14px">Q{i+1}. {ques["q"]}</div>
                <div style="font-size:13px;margin-top:5px">
                    Your answer: <b>{ans["chosen"]}</b> {"✅" if correct else "❌"}
                </div>
                {wrong_line}
                <div style="font-size:12px;color:#555;margin-top:5px;padding:6px 10px;background:rgba(0,0,0,.04);border-radius:8px">
                    💡 {ques.get("explanation","")}
                </div>
            </div>""", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 New Quiz", use_container_width=True, type="primary"):
                st.session_state.quiz = None; st.rerun()
        with col2:
            if st.button("👥 Challenge Friends", use_container_width=True):
                st.session_state.page = "friends"; st.rerun()
        return

    if q is not None and not q["done"]:
        info    = SUBJECTS.get(q.get("sub","Maths"), SUBJECTS["Maths"])
        current = q["current"]
        ques    = q["questions"][current]
        pct_bar = int((current/len(q["questions"]))*100)

        st.markdown(f"""
        <div style="background:{info["color"]}18;border-radius:14px;padding:12px 16px;
            margin-bottom:14px;display:flex;justify-content:space-between;align-items:center">
            <div>
                <span style="font-weight:800;color:{info["color"]}">{info["emoji"]} {q.get("sub","")} Quiz</span>
                <span style="font-size:12px;color:#888;margin-left:10px">{q.get("topic","")} · {q.get("difficulty","")}</span>
            </div>
            <span style="font-weight:700;color:{info["color"]}">Score: {q["score"]}/{current}</span>
        </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;font-size:12px;color:#888;margin-bottom:4px">
            <span>Question {current+1} of {len(q["questions"])}</span>
            <span>{pct_bar}% complete</span>
        </div>
        <div class="prog-bar"><div class="prog-fill" style="width:{pct_bar}%;background:{info["color"]}"></div></div>
        <br>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:#fff;border-radius:16px;padding:18px 20px;margin-bottom:14px;
            box-shadow:0 3px 16px rgba(0,0,0,0.07);font-weight:800;font-size:15px;
            color:#1A1A2E;line-height:1.55;border-left:5px solid {info["color"]}">
            Q{current+1}. {ques["q"]}
        </div>""", unsafe_allow_html=True)

        for opt_i, opt in enumerate(ques["options"]):
            if st.button(opt, key=f"opt_{current}_{opt_i}", use_container_width=True):
                q["answers"].append({"chosen":opt})
                if opt == ques["answer"]:
                    q["score"] += 1; st.toast("✅ Correct!", icon="🎉")
                else:
                    st.toast(f"❌ Correct: {ques['answer']}", icon="💡")
                q["current"] += 1
                if q["current"] >= len(q["questions"]): q["done"] = True
                st.session_state.quiz = q; st.rerun()
        return

    # ─────────────────────────────────────────────────────────────
    # INTERNAL SYLLABUS MAP  (backend only — never shown in UI)
    # Keyed as QUIZ_SYLLABUS[subject][grade] = [topic, ...]
    # ─────────────────────────────────────────────────────────────
    QUIZ_SYLLABUS = {
        "Maths": {
            "Grade 1":  ["Counting to 100","Number names","Adding single digits","Subtracting single digits","2D shapes","Measuring length","Ordinal numbers"],
            "Grade 2":  ["Place value: hundreds tens ones","Adding 2-digit numbers","Subtracting with borrowing","Times tables 2 5 10","Fractions: half quarter","Telling time","Comparing numbers"],
            "Grade 3":  ["Times tables 2-10","Long multiplication","Place value to thousands","Equivalent fractions","Perimeter","Area by counting squares","Angles: right acute obtuse"],
            "Grade 4":  ["Long multiplication 2-digit","HCF and LCM","Decimals","Algebra: simple equations","Area of triangles","Coordinates","Negative numbers"],
            "Grade 5":  ["Ratio and proportion","Percentage of a quantity","Prime factorisation","Area of circles","Algebraic expressions","Probability","Statistics: mean median mode"],
            "Grade 6":  ["Linear equations","Pythagoras theorem","Circle area and circumference","Standard form","Trigonometry basics","Scatter graphs","Simultaneous equations intro"],
            "Grade 7":  ["Simultaneous equations","Quadratic expressions","Trigonometry: sin cos tan","Vectors","Cumulative frequency","Circle theorems","Rates of change"],
            "Grade 8":  ["Quadratic formula","Circle theorems","3D trigonometry","Probability trees","Histograms","Vectors: addition and scalar","Algebraic fractions"],
            "Grade 9":  ["Binomial expansion","Differentiation intro","Integration intro","Logarithms","Geometric sequences","Functions: domain and range","Further trigonometry"],
            "Grade 10": ["Complex numbers","Matrices","Differential equations","Further statistics","Normal distribution","Coordinate geometry","Proof"],
            "O Level":  ["Paper 1 arithmetic strategies","Algebra and equations","Geometry and mensuration","Vectors and transformations","Statistics and probability","Functions","Sets"],
            "A Level":  ["Pure Maths: differentiation","Pure Maths: integration","Mechanics: kinematics","Statistics: probability distributions","Sequences and series","Coordinate geometry","Complex numbers"],
        },
        "Physics": {
            "Grade 1":  ["Push and pull forces","Light sources","Loud and soft sounds","Magnetic and non-magnetic materials"],
            "Grade 2":  ["Gravity pulls things down","Floating and sinking","Transparent and opaque","Shadows","Sound vibrations"],
            "Grade 3":  ["Types of forces","Magnetic poles","Reflection of light","Colour spectrum","How sound travels"],
            "Grade 4":  ["Simple circuits","Conductors and insulators","States of matter","Speed and distance","Electrical safety"],
            "Grade 5":  ["Newton's 3 laws of motion","Gravity and weight","Electric circuits and components","Electromagnetic fields","The solar system"],
            "Grade 6":  ["Speed distance time","Density","Pressure in fluids","Electromagnets","Conservation of energy","Sound wave properties","Reflection and refraction"],
            "Grade 7":  ["Ohm's law","Waves: amplitude frequency wavelength","Electromagnetic spectrum","Upthrust and Archimedes","Momentum","Thermal energy transfer","Static electricity"],
            "Grade 8":  ["Velocity-time graphs","Newton's three laws (extended)","Radioactivity: alpha beta gamma","Electromagnetic induction","Specific heat capacity","Gas laws","Satellites and orbits"],
            "Grade 9":  ["Scalar and vector quantities","Work energy power","Kinetic theory of matter","Series and parallel circuits","Lenses and optics","Nuclear fission and fusion","Half-life calculations"],
            "Grade 10": ["Capacitors","Particle physics","Medical imaging: X-rays MRI","Gravitational fields","SHM simple harmonic motion","Kirchhoff's laws","Semiconductor diodes"],
            "O Level":  ["Measurement and SI units","Forces and dynamics","Thermal physics","Waves and optics","Electricity and magnetism","Nuclear physics","Practical skills"],
            "A Level":  ["Quantum physics: photoelectric effect","Gravitational and electric fields","Oscillations and SHM","Nuclear physics","Astrophysics","Magnetic fields","AC circuits"],
        },
        "Chemistry": {
            "Grade 1":  ["Names of common materials","Hard and soft materials","Natural and man-made materials"],
            "Grade 2":  ["Solid liquid gas","Melting and freezing","Mixing materials"],
            "Grade 3":  ["Types of rocks","States of matter particle theory","Dissolving and solutions","Filtering"],
            "Grade 4":  ["Conductors and insulators","Reversible and irreversible changes","Mixtures and solutions","Separation techniques"],
            "Grade 5":  ["Physical vs chemical change","Acids and bases pH scale","Burning and rusting","Elements and compounds"],
            "Grade 6":  ["Periodic table introduction","Atoms and elements","Acids alkalis and indicators","Filtration distillation chromatography","Diffusion"],
            "Grade 7":  ["Atomic structure: protons neutrons electrons","Chemical equations and balancing","Metals and non-metals","Displacement reactions","Exothermic and endothermic"],
            "Grade 8":  ["Ionic bonding","Covalent bonding","Periodic table trends: Groups 1 7 0","Rates of reaction","Acids bases and salts","Electrolysis"],
            "Grade 9":  ["Mole concept and stoichiometry","Organic chemistry: alkanes alkenes","Haber process","Electrolysis calculations","Redox reactions","Equilibrium and Le Chatelier","Transition metals"],
            "Grade 10": ["Organic synthesis pathways","Enthalpy and Hess's law","Kinetics and activation energy","Quantitative electrolysis","Analytical chemistry: flame tests","Amino acids and proteins","Polymers"],
            "O Level":  ["Atomic structure and bonding","Stoichiometry","Energetics","Kinetics","Equilibrium","Organic chemistry","Metals and reactivity series"],
            "A Level":  ["Electrode potentials","Transition metal chemistry","Organic mechanisms","NMR spectroscopy","Thermodynamics","Acid-base equilibria","Polymerisation"],
        },
        "Biology": {
            "Grade 1":  ["Animals and plants","Habitats","Basic food chains","Five senses","Caring for living things"],
            "Grade 2":  ["Parts of a plant","Photosynthesis basics","Animal groups","Human body systems overview","Life cycles"],
            "Grade 3":  ["MRS GREN life processes","Food webs producers consumers","Human health and disease","Ecosystems and adaptation"],
            "Grade 4":  ["Plant and animal cells","Unicellular organisms","Pollination and seed dispersal","Carbon cycle"],
            "Grade 5":  ["Circulatory system","Respiratory system","Nervous system","Genetics and variation","Natural selection"],
            "Grade 6":  ["Cell organelles","Tissues organs organ systems","Photosynthesis equation","Digestive system in detail","Ecosystems: biotic abiotic factors"],
            "Grade 7":  ["Aerobic and anaerobic respiration","Human reproductive system","DNA structure","Disease: bacteria viruses","Carbon and nitrogen cycles"],
            "Grade 8":  ["Osmosis and diffusion","Active transport","Enzyme activity and denaturation","Immune system: antibodies phagocytes","Mitosis and meiosis","Mendelian inheritance"],
            "Grade 9":  ["Gas exchange in lungs","Transport in plants: xylem phloem","Kidney structure and ultrafiltration","Reflex arc and nervous system","Homeostasis","Monohybrid and dihybrid crosses"],
            "Grade 10": ["Sex-linked inheritance","Genetic engineering","Biotechnology: fermenters","Plant hormones: auxins","Ecology: energy flow trophic levels","Cloning techniques"],
            "O Level":  ["Cell biology and transport","Nutrition and digestion","Respiration","Gas exchange","Excretion","Coordination","Reproduction","Genetics and evolution"],
            "A Level":  ["Photosynthesis: light-dependent light-independent","Respiration: glycolysis Krebs oxidative phosphorylation","Gene expression","Immunology","Ecology and populations","Genetic technology"],
        },
        "English": {
            "Grade 1":  ["Alphabet phonics","CVC words","Sight words","Simple sentences","Capital letters and full stops"],
            "Grade 2":  ["Nouns and verbs","Adjectives","Simple and past tense","Punctuation","Short comprehension"],
            "Grade 3":  ["Parts of speech","Conjunctions and prepositions","Paragraph writing","Simile and metaphor","Skimming and scanning"],
            "Grade 4":  ["Active and passive voice","Direct and indirect speech","Essay structure","Fact and opinion","Literary devices"],
            "Grade 5":  ["Complex sentences","Relative clauses","Argumentative writing","Synonyms and antonyms","Formal and informal register"],
            "Grade 6":  ["Comprehension: inference and deduction","Narrative writing techniques","Formal letter writing","Author's viewpoint","Figurative language"],
            "Grade 7":  ["Analysing language choices","Descriptive writing: sensory detail","Persuasive writing: rhetorical devices","Comparing texts","Dramatic techniques"],
            "Grade 8":  ["Poetry analysis: form structure language","Short story: narrative voice","Analytical writing with quotations","Tone and register","Argumentative essays"],
            "Grade 9":  ["IGCSE comprehension: explicit implicit","Summary writing","Directed writing","Descriptive and narrative techniques","Persuasive writing for audience"],
            "Grade 10": ["Evaluating writer's craft","Unseen poetry analysis","Original composition commentary","Extended metaphor","Comparison of texts for purpose"],
            "O Level":  ["Comprehension and summary","Directed writing","Argumentative essays","Descriptive writing","Language analysis"],
            "A Level":  ["Language variation: regional social","Language change over time","Discourse analysis","Original writing and commentary","Critical analysis of unseen texts"],
        },
        "Computer Science": {
            "Grade 1":  ["Parts of a computer","Using a mouse","Basic keyboard skills","Computer care and safety"],
            "Grade 2":  ["Opening and closing programs","Drawing with Paint","Saving files","Printing documents"],
            "Grade 3":  ["Word processing basics","Internet safety","Searching online","Scratch: sequences and events"],
            "Grade 4":  ["Algorithms and flowcharts","Scratch: loops and conditionals","Spreadsheet formulas","Debugging programs"],
            "Grade 5":  ["Binary numbers introduction","Hardware vs software","Variables in Scratch","Networks: LAN WAN","Digital citizenship"],
            "Grade 6":  ["Python: print input variables","if elif else statements","For and while loops","Data types: int str float","Network hardware and protocols"],
            "Grade 7":  ["Binary denary hexadecimal conversion","Python lists and functions","String methods","Cybersecurity: malware phishing firewalls","Storage units: bit byte KB MB GB"],
            "Grade 8":  ["SQL: SELECT WHERE","Classes and objects OOP","File handling in Python","Exception handling try except","Software development lifecycle"],
            "Grade 9":  ["CPU fetch-execute cycle","Data compression: lossless lossy","Image representation: pixels colour depth","Sorting algorithms: bubble merge","Boolean logic and truth tables","Network topologies and protocols"],
            "Grade 10": ["Recursion in Python","Binary search and linear search","Big O complexity introduction","OOP: inheritance polymorphism","Relational databases: primary foreign keys","HTML CSS JavaScript basics"],
            "O Level":  ["Data representation","Network communication","Hardware and software","Security and privacy","Algorithm design and pseudocode","Python programming","SQL databases"],
            "A Level":  ["Processor architecture and instruction sets","Boolean algebra and logic gates","ADTs: stack queue linked list tree graph","Graph traversal BFS DFS","Functional and declarative programming","Compiler and interpreter theory"],
        },
        "Urdu": {
            "Grade 1":  ["حروفِ تہجی","حروف کی آوازیں","آسان الفاظ","تصویروں کے نام"],
            "Grade 2":  ["اسم مذکر مؤنث","واحد جمع","فعل","سادہ جملے"],
            "Grade 3":  ["اسم کی اقسام","ضمیر","صفت","زمانہ حال ماضی مستقبل","کہاوتیں"],
            "Grade 4":  ["مرکب جملے","فاعل مفعول","محاورے","مضمون نویسی","رسمی خط"],
            "Grade 5":  ["علامہ اقبالؒ کی نظمیں","حمد و نعت","افسانہ","تراکیب اضافی توصیفی"],
            "Grade 6":  ["نثری اقتباس کی تشریح","نظم کی تشریح","قواعد: فعل لازم متعدی","خلاصہ نویسی","درخواست"],
            "Grade 7":  ["غزل کا تجزیہ","ادبی اصناف","محاورے ضرب الامثال","رسمی خط","تقریر"],
            "Grade 8":  ["کلاسیکی غزل: میرؔ غالبؔ","صنعتِ تشبیہ استعارہ","علمِ عروض بحریں","تنقیدی مضمون","خبر نویسی"],
            "Grade 9":  ["نثری اصناف کا تجزیہ","علامہ اقبالؒ: بانگِ درا","میرؔ اور غالبؔ کا کلام","مضمون نویسی","قواعد کا اطلاق"],
            "Grade 10": ["اردو ادب کی تاریخ جدید دور","کلیاتِ اقبال منتخب کلام","ادبی تحریکیں","تنقید کے اصول","ترجمہ"],
            "O Level":  ["Passage comprehension in Urdu","Summary writing","Directed writing","Essay writing","Formal letters"],
            "A Level":  ["Classical poetry detailed study","Modern prose analysis","Translation Urdu to English","Language variation in Pakistan","Literary criticism"],
        },
    }

    # ─────────────────────────────────────────────────────────────
    # QUIZ SETUP — compact single-row controls
    # ─────────────────────────────────────────────────────────────
    # Row 1: four selectors side by side
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        quiz_sub = st.selectbox("Subject", list(SUBJECTS.keys()), key="quiz_sub",
                                label_visibility="visible")
    with c2:
        lvl_idx  = get_level_index(u.get("grade", "Grade 6"))
        quiz_lvl = st.selectbox("Grade", LEVELS, index=lvl_idx, key="quiz_lvl",
                                label_visibility="visible")
    with c3:
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"],
                                  index=1, key="quiz_diff",
                                  label_visibility="visible")
    with c4:
        num_qs = st.selectbox("Questions", [5, 10, 15, 20],
                              index=0, key="quiz_num",
                              label_visibility="visible")

    # Row 2: topic selector built from internal syllabus map
    syllabus_topics = QUIZ_SYLLABUS.get(quiz_sub, {}).get(quiz_lvl, [])
    topic_options   = ["— General (all topics) —"] + syllabus_topics + ["✏️ Custom topic…"]

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    selected_option = st.selectbox(
        "Topic",
        topic_options,
        key="quiz_topic_select",
        label_visibility="visible",
    )

    # Custom entry box appears only when user picks the last option
    quiz_topic = ""
    if selected_option == "✏️ Custom topic…":
        quiz_topic = st.text_input(
            "Enter your topic",
            placeholder="e.g. Projectile motion, Shakespearean sonnet, Binary trees…",
            key="quiz_custom_topic",
            label_visibility="collapsed",
        )
    elif selected_option == "— General (all topics) —":
        quiz_topic = ""
    else:
        quiz_topic = selected_option

    # Difficulty hint strip (compact, no large header)
    diff_info = {
        "Easy":   ("🟢", "Recall & recognition — perfect for quick revision."),
        "Medium": ("🟡", "Conceptual understanding & application questions."),
        "Hard":   ("🔴", "Analysis, evaluation & higher-order thinking."),
    }
    d_icon, d_text = diff_info[difficulty]
    st.markdown(
        f"<div style='background:#F8F9FA;border-radius:8px;padding:7px 12px;"
        f"font-size:12px;color:#555;margin:6px 0 10px'>"
        f"{d_icon} <b>{difficulty}:</b> {d_text}</div>",
        unsafe_allow_html=True,
    )

    if st.button("🚀 Generate Quiz", use_container_width=True, type="primary", key="gen_quiz_btn"):
        topic_str   = quiz_topic.strip() if quiz_topic.strip() else f"{quiz_sub} general topics"
        quiz_tokens = max(1200, num_qs * 220 + 300)
        with st.spinner(f"✨ Generating {num_qs} {difficulty} questions on '{topic_str}'..."):
            raw = call_ai(
                [{"role": "user", "content":
                  f"Create exactly {num_qs} {difficulty}-level multiple choice questions "
                  f"about '{topic_str}' for {quiz_lvl} {quiz_sub} students in Pakistan. "
                  f"Easy=basic recall, Medium=understanding+application, Hard=analysis+evaluation. "
                  f"Return ONLY raw JSON: "
                  f"{{\"questions\":[{{\"q\":\"question text\","
                  f"\"options\":[\"A. option\",\"B. option\",\"C. option\",\"D. option\"],"
                  f"\"answer\":\"A. option\",\"explanation\":\"why\"}}]}}"}],
                "Quiz generator. Return ONLY valid raw JSON. No backticks. No markdown.",
                quiz_tokens,
            )
        if raw.startswith("__API_KEY_MISSING__"):
            st.error("⚠️ API key not configured. Add ANTHROPIC_API_KEY or CLAUDE_API_KEY in Streamlit Secrets.")
        elif raw.startswith("__EMPTY_RESPONSE__"):
            st.error("⚠️ AI returned an empty response. Please try again.")
        elif raw.startswith("__API_ERROR__:"):
            st.error(f"⚠️ API error: {raw[14:]}")
        else:
            try:
                clean = raw.strip()
                for fence in ["```json", "```"]:
                    clean = clean.replace(fence, "")
                clean = clean.strip()
                j0 = clean.find("{"); j1 = clean.rfind("}") + 1
                if j0 >= 0 and j1 > j0:
                    clean = clean[j0:j1]
                data = json.loads(clean)
                qs   = data.get("questions", [])
                if not qs:
                    st.error("⚠️ AI returned no questions. Try a different topic.")
                else:
                    st.session_state.quiz = {
                        "questions": qs[:num_qs],
                        "current": 0, "score": 0, "answers": [], "done": False,
                        "sub": quiz_sub, "lvl": quiz_lvl,
                        "topic": topic_str, "difficulty": difficulty,
                    }
                    st.rerun()
            except Exception as _qe:
                st.error(f"⚠️ Could not parse AI response: {_qe}")
                with st.expander("Debug — AI raw output"):
                    st.code(raw[:1000])


# ─────────────────────────────────────────────────────────────────
# ONLINE FRIENDS QUIZ — Room-based multiplayer via groups.json
# Two friends each open the app, one creates a room, shares the
# 6-character code, the other joins — then each answers on their
# own device simultaneously. groups.json is the shared backend.
# ─────────────────────────────────────────────────────────────────
def _grp_save(room_id, data):
    """Write room data to groups.json."""
    groups = load_json(GROUPS_FILE)
    groups[room_id] = data
    save_json(GROUPS_FILE, groups)

def _grp_load(room_id):
    """Load room data from groups.json."""
    groups = load_json(GROUPS_FILE)
    return groups.get(room_id)

def _gen_room_id():
    """Generate a short memorable 6-char room code."""
    import string
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choices(chars, k=6))

def _cleanup_old_rooms():
    """Delete rooms older than 2 hours to keep groups.json lean."""
    groups = load_json(GROUPS_FILE)
    now    = datetime.datetime.now()
    pruned = {}
    for rid, room in groups.items():
        try:
            created = datetime.datetime.fromisoformat(room.get("created",""))
            if (now - created).total_seconds() < 7200:
                pruned[rid] = room
        except Exception:
            pass  # drop malformed entries
    if len(pruned) != len(groups):
        save_json(GROUPS_FILE, pruned)

def page_friends():
    u = st.session_state.user
    st.markdown("<div class=\"section-header purple\">👥 Online Friends Quiz</div>", unsafe_allow_html=True)

    # ── Session state shortcuts ───────────────────────────────
    my_room  = st.session_state.get("fq_room_id")       # room code I'm in
    my_role  = st.session_state.get("fq_role")          # "host" or "guest"
    my_email = u["email"]
    avatars  = ["👦","👧","🧑","👨","👩","🧒","🧑‍🎓","🧑‍💻"]

    # ── Helper: leave room ─────────────────────────────────────
    def leave_room():
        for k in ["fq_room_id","fq_role","fq_last_q","fq_answered"]:
            st.session_state.pop(k, None)
        st.rerun()

    # ── If already in a room, load its state ──────────────────
    if my_room:
        room = _grp_load(my_room)
        if not room:
            st.error("⚠️ Room not found or expired. Please create or join a new room.")
            leave_room()
            return

        phase = room.get("phase","waiting")  # waiting | playing | done

        # ── WAITING LOBBY ─────────────────────────────────────
        if phase == "waiting":
            players = room.get("players", {})
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#F5F0FF,#EDE9FE);border-radius:16px;
                padding:20px 24px;margin-bottom:18px;border:1.5px solid #A78BFA;text-align:center">
                <div style="font-size:11px;font-weight:800;color:#7C3AED;
                    text-transform:uppercase;letter-spacing:1.5px;margin-bottom:8px">Room Code</div>
                <div style="font-family:'Sora',sans-serif;font-size:48px;font-weight:900;
                    color:#5B21B6;letter-spacing:8px;margin-bottom:8px">{my_room}</div>
                <div style="font-size:13px;color:#7C3AED;font-weight:600">
                    Share this code with your friend — they enter it to join!</div>
            </div>""", unsafe_allow_html=True)

            st.markdown(f"**Players joined: {len(players)}/2**")
            for email, pdata in players.items():
                you = "  ← You" if email == my_email else ""
                st.markdown(f"- {pdata['avatar']} **{pdata['name']}**{you}")

            if len(players) < 2:
                st.info("⏳ Waiting for your friend to join with the room code...")
                time.sleep(3)
                st.rerun()
            else:
                # Both players in — host can start
                if my_role == "host":
                    st.success("✅ Friend joined! You can start the quiz.")
                    if st.button("🚀 Start Quiz!", use_container_width=True, type="primary", key="host_start"):
                        room["phase"] = "playing"
                        _grp_save(my_room, room)
                        st.rerun()
                else:
                    st.success("✅ Both players ready! Waiting for host to start...")
                    time.sleep(2)
                    st.rerun()

            if st.button("🚪 Leave Room", key="leave_waiting"):
                leave_room()
            return

        # ── PLAYING ───────────────────────────────────────────
        if phase == "playing":
            questions    = room.get("questions", [])
            players      = room.get("players", {})
            answers_all  = room.get("answers", {})        # {email: {q_idx: chosen}}
            my_answers   = answers_all.get(my_email, {})
            total_q      = len(questions)
            my_done_count = len(my_answers)

            # Which question am I on?
            my_q_idx = my_done_count  # next unanswered index

            # Scores
            def calc_score(email):
                ans = answers_all.get(email, {})
                return sum(1 for idx, chosen in ans.items()
                           if chosen == questions[int(idx)]["answer"])

            # Live scoreboard
            score_html = "<div style=\"display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap\">"
            for email, pdata in players.items():
                sc  = calc_score(email)
                done = len(answers_all.get(email,{}))
                you  = " (You)" if email == my_email else ""
                bg   = "#7C3AED" if email == my_email else "#E0D9F5"
                col  = "#fff"    if email == my_email else "#5B21B6"
                score_html += (
                    f"<div style=\"background:{bg};color:{col};border-radius:99px;"
                    f"padding:6px 16px;font-size:12px;font-weight:800\">"
                    f"{pdata['avatar']} {pdata['name']}{you}: {sc} pts · {done}/{total_q}</div>"
                )
            score_html += "</div>"
            st.markdown(score_html, unsafe_allow_html=True)

            # Show if I've finished all questions
            if my_q_idx >= total_q:
                other_done = all(
                    len(answers_all.get(e, {})) >= total_q
                    for e in players
                )
                if other_done:
                    # Everyone done — mark room done
                    room["phase"] = "done"
                    _grp_save(my_room, room)
                    st.rerun()
                else:
                    other_names = [p["name"] for e, p in players.items() if e != my_email]
                    st.success(f"✅ You've finished all {total_q} questions! Waiting for {', '.join(other_names)}...")
                    time.sleep(3)
                    st.rerun()
                return

            # Show current question
            ques    = questions[my_q_idx]
            pct_bar = int((my_q_idx / total_q) * 100)

            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;font-size:12px;
                color:#888;margin-bottom:4px">
                <span>Your Question {my_q_idx+1} of {total_q}</span>
                <span>{pct_bar}% done</span>
            </div>
            <div class="prog-bar"><div class="prog-fill"
                style="width:{pct_bar}%;background:#7C3AED"></div></div>""",
                unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background:#fff;border-radius:16px;padding:18px 20px;margin-bottom:14px;
                box-shadow:0 3px 16px rgba(0,0,0,0.07);font-weight:800;font-size:15px;
                color:#1A1A2E;border-left:5px solid #7C3AED;line-height:1.55">
                Q{my_q_idx+1}. {ques["q"]}
            </div>""", unsafe_allow_html=True)

            for opt_i, opt in enumerate(ques["options"]):
                if st.button(opt, key=f"fq_{my_q_idx}_{opt_i}", use_container_width=True):
                    # Record answer in shared room
                    room_fresh = _grp_load(my_room) or room
                    if "answers" not in room_fresh: room_fresh["answers"] = {}
                    if my_email not in room_fresh["answers"]: room_fresh["answers"][my_email] = {}
                    room_fresh["answers"][my_email][str(my_q_idx)] = opt
                    if opt == ques["answer"]:
                        st.toast("✅ Correct!", icon="🎉")
                    else:
                        st.toast(f"❌ Answer: {ques['answer']}", icon="💡")
                    _grp_save(my_room, room_fresh)
                    st.rerun()

            st.markdown("<div style=\"height:8px\"></div>", unsafe_allow_html=True)
            if st.button("🚪 Leave Quiz", use_container_width=True, type="secondary", key="leave_playing"):
                leave_room()
            return

        # ── RESULTS ───────────────────────────────────────────
        if phase == "done":
            questions   = room.get("questions", [])
            players     = room.get("players", {})
            answers_all = room.get("answers", {})
            total_q     = len(questions)

            # Save stat once
            if not room.get("_stat_saved_" + my_email):
                bump_stats(room.get("sub"), "quizzes_done")
                room_fresh = _grp_load(my_room) or room
                room_fresh["_stat_saved_" + my_email] = True
                _grp_save(my_room, room_fresh)

            st.markdown("## 🏆 Final Results")

            results = []
            for email, pdata in players.items():
                ans  = answers_all.get(email, {})
                sc   = sum(1 for idx, chosen in ans.items()
                           if chosen == questions[int(idx)]["answer"])
                pct  = int((sc/total_q)*100) if total_q else 0
                results.append({"email":email, "name":pdata["name"],
                                 "avatar":pdata["avatar"], "score":sc, "pct":pct})
            results.sort(key=lambda x: x["score"], reverse=True)

            rank_icons = ["🥇","🥈","🥉","4️⃣"]
            for i, r in enumerate(results):
                you_tag = "  ← You" if r["email"] == my_email else ""
                st.markdown(f"""
                <div class="lb-row">
                    <span class="lb-rank">{rank_icons[i]}</span>
                    <span class="lb-name">{r["avatar"]} {r["name"]}{you_tag}</span>
                    <span style="font-size:12px;color:#888">{r["pct"]}%</span>
                    <span class="lb-score">{r["score"]}/{total_q}</span>
                </div>""", unsafe_allow_html=True)

            winner = results[0]
            is_winner = (winner["email"] == my_email)
            st.markdown(f"""
            <div style="text-align:center;background:linear-gradient(135deg,#FFF8E7,#FFFBF0);
                border-radius:16px;padding:24px;margin:14px 0;border:2px solid #F5CC4A">
                <div style="font-size:44px">{"🎉" if is_winner else "👏"}</div>
                <div style="font-size:20px;font-weight:800;color:#A07820;margin-top:8px">
                    {"You win! 🏆" if is_winner else f"{winner['name']} wins!"}
                </div>
                <div style="font-size:13px;color:#888;margin-top:4px">
                    {winner["name"]}: {winner["score"]}/{total_q} correct
                </div>
            </div>""", unsafe_allow_html=True)

            st.markdown("### 📋 Answer Review")
            my_ans = answers_all.get(my_email, {})
            for i, ques in enumerate(questions):
                chosen  = my_ans.get(str(i), "—")
                correct = chosen == ques["answer"]
                bg      = "#F0FDF4" if correct else "#FFF1EE"
                border  = "#059669" if correct else "#E8472A"
                wrong   = "" if correct else f"<div style=\"font-size:12px;color:#059669;margin-top:3px\">✅ {ques['answer']}</div>"
                st.markdown(f"""
                <div style="background:{bg};border:1.5px solid {border};border-radius:12px;
                    padding:12px 14px;margin-bottom:8px">
                    <div style="font-weight:700;font-size:13px">Q{i+1}. {ques["q"]}</div>
                    <div style="font-size:12px;margin-top:4px">
                        Your answer: <b>{chosen}</b> {"✅" if correct else "❌"}</div>
                    {wrong}
                    <div style="font-size:11px;color:#666;margin-top:4px;padding:5px 8px;
                        background:rgba(0,0,0,.04);border-radius:6px">💡 {ques.get("explanation","")}</div>
                </div>""", unsafe_allow_html=True)

            if st.button("🔄 Play Again", use_container_width=True, type="primary", key="play_again"):
                leave_room()
            return

    # ── NO ROOM — Show Create / Join tabs ─────────────────────
    _cleanup_old_rooms()

    st.markdown("""
    <div style="background:linear-gradient(135deg,#F5F0FF,#EDE9FE);border-radius:14px;
        padding:14px 18px;margin-bottom:18px;font-size:13px;color:#5B21B6;
        border-left:4px solid #7C3AED">
        🌐 <b>Online Friends Quiz</b> — Play with a friend on any device, anywhere!
        One person creates a room, shares the code, and both answer simultaneously.
        The fastest and most accurate player wins!
    </div>""", unsafe_allow_html=True)

    tab_create, tab_join = st.tabs(["➕  Create Room", "🔗  Join Room"])

    with tab_create:
        st.markdown("#### 📚 Quiz Settings")
        c1, c2 = st.columns(2)
        with c1:
            grp_sub = st.selectbox("Subject", list(SUBJECTS.keys()), key="grp_sub")
        with c2:
            lvl_idx = get_level_index(u.get("grade","Grade 6"))
            grp_lvl = st.selectbox("Grade", LEVELS, index=lvl_idx, key="grp_lvl")

        grp_topic = st.text_input("Topic (optional)", placeholder="e.g. Photosynthesis...", key="grp_topic")
        c3, c4 = st.columns(2)
        with c3:
            grp_diff = st.selectbox("Difficulty", ["Easy","Medium","Hard"], index=1, key="grp_diff")
        with c4:
            grp_num = st.selectbox("Questions", [5, 10, 15], index=0, key="grp_num")

        if st.button("🚀 Create Room & Generate Quiz", use_container_width=True,
                     type="primary", key="create_room_btn"):
            topic_str  = grp_topic.strip() if grp_topic.strip() else f"{grp_sub} general"
            grp_tokens = max(1200, grp_num * 220 + 300)
            with st.spinner(f"Generating {grp_num} questions..."):
                raw = call_ai(
                    [{"role":"user","content":
                      f"Create exactly {grp_num} {grp_diff}-level MCQ questions about '{topic_str}' "
                      f"for {grp_lvl} {grp_sub} students. "
                      f"Return ONLY raw JSON: {{\"questions\":[{{\"q\":\"...\","
                      f"\"options\":[\"A. ...\",\"B. ...\",\"C. ...\",\"D. ...\"],"
                      f"\"answer\":\"A. ...\",\"explanation\":\"...\"}}]}}"}],
                    "Quiz generator. Return ONLY valid raw JSON.", grp_tokens
                )
            if raw.startswith(("__API_KEY_MISSING__","__EMPTY_RESPONSE__","__API_ERROR__:")):
                st.error(f"⚠️ AI error: {raw}")
            else:
                try:
                    clean = raw.strip()
                    for fence in ["```json","```"]:
                        clean = clean.replace(fence,"")
                    clean = clean.strip()
                    j0 = clean.find("{"); j1 = clean.rfind("}") + 1
                    if j0 >= 0 and j1 > j0: clean = clean[j0:j1]
                    data      = json.loads(clean)
                    questions = data.get("questions",[])[:grp_num]
                    if not questions: raise ValueError("No questions returned")
                    room_id   = _gen_room_id()
                    room_data = {
                        "created":  datetime.datetime.now().isoformat(),
                        "host":     my_email,
                        "phase":    "waiting",
                        "sub":      grp_sub,
                        "lvl":      grp_lvl,
                        "topic":    topic_str,
                        "difficulty": grp_diff,
                        "questions": questions,
                        "answers":  {},
                        "players":  {
                            my_email: {
                                "name":   u["name"],
                                "avatar": u.get("avatar","👦"),
                                "joined": datetime.datetime.now().isoformat(),
                            }
                        }
                    }
                    _grp_save(room_id, room_data)
                    st.session_state.fq_room_id = room_id
                    st.session_state.fq_role    = "host"
                    st.rerun()
                except Exception as e:
                    st.error(f"⚠️ Could not generate quiz: {e}")
                    with st.expander("Debug"): st.code(raw[:500])

    with tab_join:
        st.markdown("#### 🔗 Enter the room code your friend shared with you")
        join_code = st.text_input("Room Code", placeholder="e.g. AB3X7K",
                                  max_chars=6, key="join_code_input").strip().upper()
        if st.button("🚪 Join Room", use_container_width=True,
                     type="primary", key="join_room_btn"):
            if not join_code:
                st.error("Please enter a room code.")
            else:
                room = _grp_load(join_code)
                if not room:
                    st.error("⚠️ Room not found. Check the code and try again.")
                elif room.get("phase") != "waiting":
                    st.error("⚠️ This quiz has already started or finished.")
                elif my_email in room.get("players",{}):
                    # Rejoin own room
                    st.session_state.fq_room_id = join_code
                    st.session_state.fq_role    = "host" if room.get("host")==my_email else "guest"
                    st.rerun()
                elif len(room.get("players",{})) >= 2:
                    st.error("⚠️ Room is full (2 players max).")
                else:
                    room["players"][my_email] = {
                        "name":   u["name"],
                        "avatar": u.get("avatar","👦"),
                        "joined": datetime.datetime.now().isoformat(),
                    }
                    _grp_save(join_code, room)
                    st.session_state.fq_room_id = join_code
                    st.session_state.fq_role    = "guest"
                    st.rerun()


# ─────────────────────────────────────────────────────────────────
# IMAGE GENERATOR
# ─────────────────────────────────────────────────────────────────
def page_image():
    # ══════════════════════════════════════════════════════════════
    # SESSION STATE INIT
    # ══════════════════════════════════════════════════════════════
    for _k, _v in [
        ("img_last_svg",    None),   # cached SVG string of last result
        ("img_last_prompt", ""),     # prompt that produced it
        ("img_last_style",  ""),     # style label used
        ("img_regenerate",  False),  # flag to re-trigger generation
    ]:
        if _k not in st.session_state:
            st.session_state[_k] = _v

    u = st.session_state.user

    # ══════════════════════════════════════════════════════════════
    # STYLE DEFINITIONS  (compact pills, not a dropdown)
    # ══════════════════════════════════════════════════════════════
    STYLES = {
        "📐 Diagram":   ("a clean labeled educational diagram with arrows, colorful sections, white background",     "#2563EB"),
        "🎨 Cartoon":   ("a bright fun cartoon illustration with cheerful bold colors suitable for students",         "#E8472A"),
        "🔬 Realistic": ("a detailed realistic scientific illustration like a textbook diagram, accurate and labeled", "#059669"),
        "🤖 3D / AI":   ("a futuristic 3D-rendered AI-generated digital art style with glowing elements and depth",   "#7C3AED"),
        "🎌 Sci-Fi":    ("a sci-fi style illustration with neon accents, space themes, and high-tech elements",       "#B45309"),
    }
    STYLE_KEYS = list(STYLES.keys())

    SUGGESTIONS = [
        "Solar system diagram",
        "Human heart anatomy",
        "Photosynthesis process",
        "Water cycle",
        "Plant cell structure",
        "Pyramid / food chain",
        "AI robot",
        "Atom structure",
    ]

    # ── Read selected style from session state (default = first)
    if "img_style_sel" not in st.session_state:
        st.session_state.img_style_sel = STYLE_KEYS[0]

    # ══════════════════════════════════════════════════════════════
    # PROMPT INPUT AREA
    # ══════════════════════════════════════════════════════════════

    # Suggestion chips — clicking one fills the prompt
    st.markdown(
        "<div style='font-size:12px;font-weight:600;color:#888;"
        "margin-bottom:6px;letter-spacing:.03em'>✨ Quick ideas</div>",
        unsafe_allow_html=True
    )
    chip_cols = st.columns(len(SUGGESTIONS))
    for ci, sug in enumerate(SUGGESTIONS):
        with chip_cols[ci]:
            if st.button(sug, key=f"sug_{ci}", use_container_width=True):
                st.session_state["img_prompt_val"] = sug

    # Carry suggestion into text area via session state
    if "img_prompt_val" not in st.session_state:
        st.session_state.img_prompt_val = ""

    prompt = st.text_area(
        "Prompt",
        value=st.session_state.img_prompt_val,
        placeholder="Describe the image you want to generate...",
        height=110,
        key="img_prompt_area",
        label_visibility="collapsed",
    )

    # Style selector pills
    st.markdown(
        "<div style='font-size:12px;font-weight:600;color:#888;"
        "margin:8px 0 4px;letter-spacing:.03em'>🎨 Style</div>",
        unsafe_allow_html=True
    )
    scols = st.columns(len(STYLE_KEYS))
    for si, sk in enumerate(STYLE_KEYS):
        with scols[si]:
            _, sc_hex = STYLES[sk]
            is_active = st.session_state.img_style_sel == sk
            btn_type  = "primary" if is_active else "secondary"
            if st.button(sk, key=f"style_{si}", use_container_width=True, type=btn_type):
                st.session_state.img_style_sel = sk
                st.rerun()

    active_style  = st.session_state.img_style_sel
    style_hint, _ = STYLES[active_style]

    # Generate button
    do_generate = st.button(
        "✦ Generate Image",
        use_container_width=True,
        type="primary",
        key="img_gen_btn",
    )

    # Also trigger if Regenerate was pressed last cycle
    if st.session_state.img_regenerate:
        do_generate = True
        st.session_state.img_regenerate = False

    # ══════════════════════════════════════════════════════════════
    # GENERATION LOGIC
    # ══════════════════════════════════════════════════════════════
    if do_generate:
        final_prompt = (prompt or st.session_state.img_last_prompt).strip()
        if not final_prompt:
            st.warning("Please enter a description or pick a suggestion above.")
        else:
            prog = st.progress(0,  text="🎨 Planning diagram…")
            time.sleep(0.3)
            prog.progress(20, text="✏️ Drawing shapes…")
            time.sleep(0.3)
            prog.progress(50, text="🎨 Adding colours & labels…")

            system_msg = (
                "You are an expert SVG illustrator who creates educational diagrams. "
                "STRICT OUTPUT RULES:\n"
                "1. Output ONLY the SVG code. No markdown. No backticks. No explanations.\n"
                "2. Start with exactly: <svg\n"
                "3. End with exactly: </svg>\n"
                "4. Use: xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 700 500\" width=\"700\" height=\"500\"\n"
                "5. Include <defs> with at least 3 linearGradient definitions.\n"
                "6. Bold title at top (y=35, font-size=24, font-weight=bold, text-anchor=middle, x=350).\n"
                "7. BRIGHT colors — use gradient fills on all major shapes.\n"
                "8. Include 20+ visual elements: shapes, labels, arrows.\n"
                f"9. Style: {style_hint}\n"
                "10. Every component must have a clear text label.\n"
                "11. Make it look like a professional educational poster.\n"
                "12. DO NOT use any xlink:href or external images."
            )
            user_msg = (
                f"Create a detailed colourful educational SVG illustration.\n"
                f"TOPIC: {final_prompt}\nSTYLE: {style_hint}\n\n"
                f"Include: gradient background, bold title, labeled components, arrows.\n"
                f"Output ONLY the SVG. Start with <svg and end with </svg>."
            )

            raw = call_ai_svg([{"role": "user", "content": user_msg}], system_msg)
            prog.progress(90, text="✨ Finishing touches…")
            time.sleep(0.3)
            prog.progress(100, text="✅ Done!")
            time.sleep(0.2)
            prog.empty()

            # Parse SVG
            cleaned = raw
            for fence in ["```svg", "```xml", "```html", "```"]:
                cleaned = cleaned.replace(fence, "")
            cleaned   = cleaned.strip()
            svg_start = cleaned.find("<svg")
            svg_end   = cleaned.rfind("</svg>")

            if svg_start >= 0 and svg_end >= 0:
                final_svg = cleaned[svg_start:svg_end + 6]

                # Cache in session state (survives rerun)
                st.session_state.img_last_svg    = final_svg
                st.session_state.img_last_prompt = final_prompt
                st.session_state.img_last_style  = active_style
                st.session_state.img_prompt_val  = final_prompt

                # Persist to images.json
                imgs  = load_json(IMAGES_FILE)
                email = u["email"]
                if email not in imgs:
                    imgs[email] = []
                imgs[email].insert(0, {
                    "id":      str(int(time.time())),
                    "svg":     final_svg,
                    "prompt":  final_prompt,
                    "subject": "",
                    "level":   "",
                    "style":   active_style,
                    "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                })
                save_json(IMAGES_FILE, imgs)

                # Update user stats + badges
                users = load_json(USERS_FILE)
                eu    = users.get(u["email"], u)
                eu.setdefault("stats", init_stats())
                eu["stats"]["images"] = eu["stats"].get("images", 0) + 1
                eu, new_b = check_badges(eu)
                users[u["email"]] = eu
                save_json(USERS_FILE, users)
                st.session_state.user = eu
                for b in new_b:
                    st.toast(f"🏆 Badge: {b['icon']} {b['name']}!", icon="🎉")
            else:
                st.error("⚠️ Could not generate image. Try rephrasing your description.")
                with st.expander("Debug"):
                    st.code(raw[:600])

    # ══════════════════════════════════════════════════════════════
    # IMAGE RESULT DISPLAY  (persists across reruns via session state)
    # ══════════════════════════════════════════════════════════════
    cached_svg = st.session_state.get("img_last_svg")
    if cached_svg:
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        # Centred image card
        st.markdown(
            "<div style='background:#fff;border-radius:16px;"
            "box-shadow:0 2px 16px rgba(0,0,0,0.08);padding:16px;"
            "margin:0 auto;max-width:740px'>",
            unsafe_allow_html=True
        )
        st.components.v1.html(cached_svg, height=520, scrolling=False)
        st.markdown("</div>", unsafe_allow_html=True)

        # Utility buttons: Download | Regenerate
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        ub1, ub2 = st.columns(2)
        with ub1:
            b64svg = base64.b64encode(cached_svg.encode()).decode()
            st.markdown(
                f"<a href='data:image/svg+xml;base64,{b64svg}' "
                f"download='zm_diagram.svg' "
                f"style='display:flex;align-items:center;justify-content:center;gap:8px;"
                f"padding:10px 0;background:#7C3AED;color:#fff;border-radius:10px;"
                f"font-weight:700;font-size:14px;text-decoration:none;width:100%;'>"
                f"⬇️ Download Image</a>",
                unsafe_allow_html=True
            )
        with ub2:
            if st.button("🔄 Regenerate", key="img_regen_btn",
                         use_container_width=True):
                st.session_state.img_regenerate = True
                st.rerun()

        # Caption
        cap_prompt = st.session_state.img_last_prompt
        cap_style  = st.session_state.img_last_style
        st.markdown(
            f"<div style='text-align:center;font-size:11px;color:#aaa;margin-top:6px'>"
            f"{cap_style} · {cap_prompt[:80]}{'…' if len(cap_prompt)>80 else ''}"
            f"</div>",
            unsafe_allow_html=True
        )

    # ══════════════════════════════════════════════════════════════
    # GALLERY  — previous images, compact 2-column grid
    # ══════════════════════════════════════════════════════════════
    imgs      = load_json(IMAGES_FILE)
    user_imgs = imgs.get(u["email"], [])
    # Exclude the currently displayed image from gallery to avoid duplication
    cached_id = None
    if user_imgs and cached_svg:
        cached_id = user_imgs[0]["id"] if user_imgs[0]["svg"] == cached_svg else None
    gallery_imgs = [x for x in user_imgs if x["id"] != cached_id][:8]

    if gallery_imgs:
        st.markdown(
            "<div style='height:6px'></div>"
            "<div style='font-size:13px;font-weight:700;color:#555;"
            "margin:12px 0 6px'>🖼️ Previous Images</div>",
            unsafe_allow_html=True
        )
        for i in range(0, len(gallery_imgs), 2):
            gcols = st.columns(2)
            for j, gc in enumerate(gcols):
                if i + j < len(gallery_imgs):
                    img = gallery_imgs[i + j]
                    with gc:
                        preview = img["prompt"][:55] + ("…" if len(img["prompt"]) > 55 else "")
                        st.markdown(
                            f"<div style='background:#fff;border-radius:12px;"
                            f"padding:10px 12px;box-shadow:0 1px 8px rgba(0,0,0,0.06);"
                            f"border:1px solid #F0F0F5;margin-bottom:8px'>"
                            f"<div style='font-size:10px;font-weight:700;color:#7C3AED;"
                            f"margin-bottom:4px'>{img.get('style','—')} · {img['created']}</div>"
                            f"<div style='font-size:12px;color:#444'>📝 {preview}</div>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                        with st.expander("🔍 View"):
                            st.components.v1.html(img["svg"], height=440, scrolling=False)
                            gd1, gd2 = st.columns(2)
                            with gd1:
                                b64g   = base64.b64encode(img["svg"].encode()).decode()
                                img_id = img["id"]
                                st.markdown(
                                    f"<a href='data:image/svg+xml;base64,{b64g}' "
                                    f"download='zm_{img_id}.svg' "
                                    f"style='display:inline-block;padding:6px 14px;"
                                    f"background:#7C3AED;color:#fff;border-radius:8px;"
                                    f"font-weight:700;font-size:12px;text-decoration:none'>"
                                    f"⬇️ Download</a>",
                                    unsafe_allow_html=True
                                )
                            with gd2:
                                if st.button("🗑️ Delete", key=f"del_img_{img['id']}",
                                             use_container_width=True):
                                    imgs_f = load_json(IMAGES_FILE)
                                    imgs_f[u["email"]] = [
                                        x for x in imgs_f.get(u["email"], [])
                                        if x["id"] != img["id"]
                                    ]
                                    save_json(IMAGES_FILE, imgs_f)
                                    st.rerun()


# ─────────────────────────────────────────────────────────────────
# SYLLABUS
# ─────────────────────────────────────────────────────────────────
def page_syllabus():
    # ══════════════════════════════════════════════════════════════
    # LOCAL HELPERS
    # ══════════════════════════════════════════════════════════════
    SUBJ_KEY_MAP = {
        "Mathematics": "Maths", "Maths": "Maths",
        "Physics": "Physics", "Chemistry": "Chemistry",
        "Biology": "Biology", "Science": "Biology",
        "English": "English", "English Language": "English",
        "Computer Science": "Computer Science",
        "Urdu": "Urdu", "Islamiyat": "English",
    }

    def _save_user(eu):
        users = load_json(USERS_FILE)
        users[eu["email"]] = eu
        save_json(USERS_FILE, users)
        st.session_state.user = eu

    def _ensure_fields(u):
        dirty = False
        if "studied_topics" not in u:
            u["studied_topics"] = {}; dirty = True
        if "topic_dates" not in u:
            u["topic_dates"] = {}; dirty = True
        if dirty:
            _save_user(u)
        return u

    def _pace_per_day(u, syl_key):
        td = u.get("topic_dates", {}).get(syl_key, {})
        if not td:
            return 2.0
        dates = sorted(set(td.values()))
        if len(dates) < 2:
            return max(1.0, float(len(td)))
        try:
            span = max(1, (datetime.date.fromisoformat(dates[-1])
                          - datetime.date.fromisoformat(dates[0])).days)
            return max(0.5, len(td) / span)
        except Exception:
            return 2.0

    def _toggle_done(u, syl_key, topic_key):
        """Toggle a topic's completion state; returns updated user object."""
        users    = load_json(USERS_FILE)
        eu       = _ensure_fields(users.get(u["email"], u))
        st_map   = eu.get("studied_topics", {})
        tlist    = list(st_map.get(syl_key, []))
        td_map   = eu.get("topic_dates", {})
        td_syl   = dict(td_map.get(syl_key, {}))
        today    = datetime.date.today().isoformat()
        if topic_key in tlist:
            tlist.remove(topic_key)
            td_syl.pop(topic_key, None)
        else:
            tlist.append(topic_key)
            td_syl[topic_key] = today
        st_map[syl_key]      = tlist
        td_map[syl_key]      = td_syl
        eu["studied_topics"] = st_map
        eu["topic_dates"]    = td_map
        eu, new_b = check_badges(eu)
        _save_user(eu)
        for b in new_b:
            st.toast(f"🏆 Badge: {b['icon']} {b['name']}!", icon="🎉")
        return eu

    # ══════════════════════════════════════════════════════════════
    # SESSION STATE KEYS for this page
    #   syl_view        : "list" | "detail"
    #   syl_topic_idx   : int  — flat index into all_topics list
    #   syl_detail_content : str | None  — cached AI explanation
    #   syl_detail_for  : str | None  — topic_key the content belongs to
    # ══════════════════════════════════════════════════════════════
    for _k, _v in [("syl_view", "list"), ("syl_topic_idx", 0),
                   ("syl_detail_content", None), ("syl_detail_for", None)]:
        if _k not in st.session_state:
            st.session_state[_k] = _v

    # ══════════════════════════════════════════════════════════════
    # SELECTOR ROW  ── Curriculum | Grade | Subject
    # ══════════════════════════════════════════════════════════════
    u = _ensure_fields(st.session_state.user)

    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        curriculum = st.selectbox("Curriculum", ["Cambridge (Pakistan)"],
                                  key="syl_curr", label_visibility="visible")
    with sc2:
        def_grade     = normalise_level(u.get("grade", "Grade 8"))
        def_grade_idx = get_level_index(def_grade)
        sel_grade = st.selectbox("Grade", LEVELS, index=def_grade_idx,
                                 key="syl_grade_sel", label_visibility="visible")
    with sc3:
        avail_subs = CAMBRIDGE_SUBJECTS.get(sel_grade, list(SUBJECTS.keys()))
        sel_sub = st.selectbox("Subject", avail_subs,
                               key="syl_sub_sel", label_visibility="visible")

    st.session_state.syl_subject = sel_sub

    # Persist grade change
    if sel_grade != normalise_level(u.get("grade", "")):
        _tmp = load_json(USERS_FILE)
        if u["email"] in _tmp:
            _tmp[u["email"]]["grade"] = sel_grade
            save_json(USERS_FILE, _tmp)
            st.session_state.user["grade"] = sel_grade

    # When selectors change, reset to list view
    _sel_sig = f"{sel_grade}|{sel_sub}"
    if st.session_state.get("_syl_sel_sig") != _sel_sig:
        st.session_state["_syl_sel_sig"] = _sel_sig
        st.session_state.syl_view        = "list"
        st.session_state.syl_detail_content = None
        st.session_state.syl_detail_for     = None

    # ── Subject metadata ──────────────────────────────────────────
    subj_key  = SUBJ_KEY_MAP.get(sel_sub, "Maths")
    info      = SUBJECTS.get(subj_key, {"emoji": "📚", "color": "#2563EB"})
    sub_color = info["color"]
    sub_emoji = info["emoji"]

    # ── Load units ────────────────────────────────────────────────
    curr = CAMBRIDGE_CURRICULUM.get(subj_key, {}).get(sel_grade, {})
    if not curr:
        for _ao, _an in _LEVEL_ALIAS.items():
            if _an == sel_grade:
                curr = CAMBRIDGE_CURRICULUM.get(subj_key, {}).get(_ao, {})
                if curr: break

    board = curr.get("board", "Cambridge / Pakistan National Curriculum")
    units = curr.get("units", [])

    if not units:
        st.info(f"📋 No pre-loaded syllabus for **{sel_sub} — {sel_grade}**.")
        if st.button(f"💬 Ask Ustad about {sel_sub} {sel_grade}",
                     use_container_width=True, type="primary"):
            st.session_state.subject = subj_key
            st.session_state.chat_messages = [{"role": "user", "content":
                f"Give me a full overview of the {sel_sub} syllabus for {sel_grade} "
                f"in Pakistan. List all main units and topics."}]
            st.session_state.page = "chat"; st.rerun()
        return

    # ── Flat topic list: [{unit_name, topic, topic_key, unit_idx, topic_idx_in_unit}]
    all_topics = []
    for ui, unit in enumerate(units):
        for ti, topic in enumerate(unit["topics"]):
            all_topics.append({
                "unit_name":       unit["unit"],
                "topic":           topic,
                "topic_key":       f"{unit['unit']}::{topic}",
                "unit_idx":        ui,
                "topic_idx_local": ti,
            })

    # ── Coverage stats ────────────────────────────────────────────
    syl_key     = f"{subj_key}_{sel_grade}"
    done_set    = set(u.get("studied_topics", {}).get(syl_key, []))
    total       = len(all_topics)
    done_count  = sum(1 for t in all_topics if t["topic_key"] in done_set)
    remaining   = total - done_count
    pct         = int(done_count / max(total, 1) * 100)
    pace        = _pace_per_day(u, syl_key)
    days_left   = max(1, round(remaining / pace)) if remaining > 0 else 0
    finish_str  = (datetime.date.today() + datetime.timedelta(days=days_left)).strftime("%d %b %Y") \
                   if days_left > 0 else "Done!"
    pace_str    = f"{pace:.1f} topics/day" if pace != int(pace) else f"{int(pace)} topics/day"
    pace_src    = "📈 your history" if u.get("topic_dates", {}).get(syl_key) else "📌 default"

    pbar_color  = "#059669" if pct >= 80 else "#F59E0B" if pct >= 40 else sub_color
    eta_label   = "🏆 Done!" if days_left == 0 else (f"{days_left}d left")

    # ── Compact progress strip ────────────────────────────────────
    st.markdown(f"""
    <div style="background:#fff;border-radius:12px;padding:12px 16px;
        box-shadow:0 1px 8px rgba(0,0,0,0.06);margin:6px 0 10px;
        display:flex;align-items:center;gap:14px;flex-wrap:wrap">
        <div style="font-size:20px">{sub_emoji}</div>
        <div style="flex:1;min-width:160px">
            <div style="display:flex;justify-content:space-between;
                font-size:12px;font-weight:700;color:#555;margin-bottom:4px">
                <span>{sel_sub} · {sel_grade}</span>
                <span style="color:{pbar_color}">{pct}% covered</span>
            </div>
            <div style="background:#F3F4F6;border-radius:6px;height:7px;overflow:hidden">
                <div style="width:{pct}%;background:{pbar_color};
                    height:7px;border-radius:6px"></div>
            </div>
        </div>
        <div style="display:flex;gap:10px;flex-wrap:wrap">
            <div style="background:{sub_color}0f;border:1px solid {sub_color}2a;
                border-radius:8px;padding:5px 12px;text-align:center;min-width:60px">
                <div style="font-size:16px;font-weight:900;color:{sub_color}">{done_count}</div>
                <div style="font-size:10px;color:#888">done</div>
            </div>
            <div style="background:#FFF7ED;border:1px solid #FED7AA;
                border-radius:8px;padding:5px 12px;text-align:center;min-width:60px">
                <div style="font-size:16px;font-weight:900;color:#EA580C">{remaining}</div>
                <div style="font-size:10px;color:#888">left</div>
            </div>
            <div style="background:#F0FDF4;border:1px solid #BBF7D0;
                border-radius:8px;padding:5px 12px;text-align:center;min-width:60px">
                <div style="font-size:14px;font-weight:900;color:#059669">{eta_label}</div>
                <div style="font-size:10px;color:#888">{pace_str}</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════
    # VIEW: TOPIC DETAIL
    # ══════════════════════════════════════════════════════════════
    if st.session_state.syl_view == "detail":
        idx     = st.session_state.syl_topic_idx
        idx     = max(0, min(idx, total - 1))
        t_info  = all_topics[idx]
        t_key   = t_info["topic_key"]
        t_name  = t_info["topic"]
        u_name  = t_info["unit_name"]
        is_done = t_key in done_set

        # ── Navigation bar ────────────────────────────────────────
        nav1, nav2, nav3 = st.columns([2, 4, 2])
        with nav1:
            if st.button("◀ Back", key="syl_back", use_container_width=True):
                st.session_state.syl_view = "list"
                st.rerun()
        with nav2:
            st.markdown(
                f"<div style='text-align:center;font-size:12px;color:#888;"
                f"padding:6px 0'>{idx+1} / {total} &nbsp;·&nbsp; {u_name}</div>",
                unsafe_allow_html=True
            )
        with nav3:
            next_disabled = (idx >= total - 1)
            if st.button("Next ▶", key="syl_next", use_container_width=True,
                         disabled=next_disabled):
                st.session_state.syl_topic_idx    = idx + 1
                st.session_state.syl_detail_content = None
                st.session_state.syl_detail_for     = None
                st.rerun()

        # ── Topic header ──────────────────────────────────────────
        done_bg  = "#F0FDF4" if is_done else "#fff"
        done_bdr = "#6EE7B7" if is_done else f"{sub_color}44"
        st.markdown(f"""
        <div style="background:{done_bg};border:2px solid {done_bdr};
            border-radius:14px;padding:14px 18px;margin:6px 0 12px">
            <div style="font-size:11px;font-weight:600;color:{sub_color};
                text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px">
                {u_name}
            </div>
            <div style="font-size:17px;font-weight:800;color:#1A1A2E;line-height:1.35">
                {'✅ ' if is_done else '📖 '}{t_name}
            </div>
        </div>""", unsafe_allow_html=True)

        # ── Action row ────────────────────────────────────────────
        a1, a2, a3 = st.columns(3)
        with a1:
            done_lbl = "✅ Mark Undone" if is_done else "✓ Mark Complete"
            if st.button(done_lbl, key="syl_mark", use_container_width=True,
                         type="primary" if not is_done else "secondary"):
                u = _toggle_done(u, syl_key, t_key)
                done_set = set(u.get("studied_topics", {}).get(syl_key, []))
                st.rerun()
        with a2:
            if st.button("💬 Ask Ustad", key="syl_ask_detail", use_container_width=True):
                st.session_state.subject = subj_key
                st.session_state.level   = sel_grade
                st.session_state.chat_messages = [{"role": "user",
                    "content": f"Explain this topic from my {sel_grade} {sel_sub} "
                               f"syllabus in detail: {t_name}"}]
                st.session_state.session_id = None
                st.session_state.page = "chat"; st.rerun()
        with a3:
            load_lbl = "🔄 Reload" if st.session_state.syl_detail_for == t_key else "📖 Load Notes"
            if st.button(load_lbl, key="syl_load_notes", use_container_width=True):
                st.session_state.syl_detail_content = None  # force reload
                st.session_state.syl_detail_for     = None

        # ── Load AI explanation (cached per topic_key) ────────────
        if st.session_state.syl_detail_for != t_key:
            with st.spinner(f"📖 Loading notes for '{t_name}'…"):
                raw_exp = call_ai(
                    [{"role": "user", "content":
                      f"Explain '{t_name}' from {sel_grade} {sel_sub} ({board}) in Pakistan. "
                      f"Structure your response as:\n"
                      f"**Overview** (2-3 sentences)\n"
                      f"**Key Concepts** (bullet points)\n"
                      f"**Examples / Worked Problems** (at least 1 concrete example)\n"
                      f"**Important Facts to Remember** (bullet points)\n"
                      f"Keep it concise, exam-focused, and suitable for a student."}],
                    f"You are an expert {sel_sub} teacher for {sel_grade} in Pakistan. "
                    f"Explain clearly and concisely. Use markdown.", 900
                )
            st.session_state.syl_detail_content = raw_exp
            st.session_state.syl_detail_for     = t_key

        content = st.session_state.syl_detail_content or ""
        if content.startswith("__API_KEY_MISSING__"):
            st.warning("⚠️ Add ANTHROPIC_API_KEY to Streamlit secrets to load notes.")
        elif content.startswith(("__EMPTY_RESPONSE__", "__API_ERROR__:")):
            st.warning(f"⚠️ Could not load notes: {content}")
        else:
            st.markdown(
                f"<div style='background:#FAFAFA;border-radius:12px;"
                f"padding:16px 18px;border:1px solid #E5E7EB;"
                f"font-size:14px;line-height:1.75;color:#1A1A2E;margin-top:4px'>"
                f"{content}</div>",
                unsafe_allow_html=True
            )

        # ── Bottom navigation ─────────────────────────────────────
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        bn1, bn2, bn3 = st.columns([2, 4, 2])
        with bn1:
            if idx > 0:
                if st.button("◀ Prev Topic", key="syl_prev_bot", use_container_width=True):
                    st.session_state.syl_topic_idx      = idx - 1
                    st.session_state.syl_detail_content = None
                    st.session_state.syl_detail_for     = None
                    st.rerun()
        with bn3:
            if idx < total - 1:
                if st.button("Next Topic ▶", key="syl_next_bot", use_container_width=True,
                             type="primary"):
                    st.session_state.syl_topic_idx      = idx + 1
                    st.session_state.syl_detail_content = None
                    st.session_state.syl_detail_for     = None
                    st.rerun()

        return  # ← don't render list view below

    # ══════════════════════════════════════════════════════════════
    # VIEW: TOPIC LIST  (default)
    # ══════════════════════════════════════════════════════════════
    for ui, unit in enumerate(units):
        unit_tkeys      = [f"{unit['unit']}::{t}" for t in unit["topics"]]
        unit_done       = sum(1 for tk in unit_tkeys if tk in done_set)
        unit_total      = len(unit["topics"])
        unit_pct        = int(unit_done / max(unit_total, 1) * 100)
        unit_icon       = "✅" if unit_pct == 100 else "🔵" if unit_pct > 0 else "⚪"

        with st.expander(
            f"{unit_icon}  Unit {ui+1}: {unit['unit']}  ({unit_done}/{unit_total})",
            expanded=(ui == 0)
        ):
            # Unit progress bar
            st.markdown(
                f"<div style='background:#F3F4F6;border-radius:4px;height:5px;"
                f"overflow:hidden;margin-bottom:10px'>"
                f"<div style='width:{unit_pct}%;background:{sub_color};"
                f"height:5px;border-radius:4px'></div></div>",
                unsafe_allow_html=True
            )

            # Topic rows — each is a clickable module card
            for ti, topic in enumerate(unit["topics"]):
                topic_key = f"{unit['unit']}::{topic}"
                is_done   = topic_key in done_set

                # Compute flat index
                flat_idx = next(
                    i for i, t in enumerate(all_topics)
                    if t["topic_key"] == topic_key
                )

                row_bg  = "#F0FDF4" if is_done else "#fff"
                row_bdr = "#6EE7B7" if is_done else "#E5E7EB"
                lbl_col = "#059669" if is_done else "#1A1A2E"
                num_bg  = sub_color if not is_done else "#059669"

                # Module card row: number badge | topic name | Open button | Mark button
                mc1, mc2, mc3 = st.columns([5, 1, 1])
                with mc1:
                    st.markdown(
                        f"<div style='background:{row_bg};border:1px solid {row_bdr};"
                        f"border-radius:10px;padding:8px 12px;display:flex;"
                        f"align-items:center;gap:10px;cursor:pointer'>"
                        f"<div style='background:{num_bg};color:#fff;border-radius:6px;"
                        f"width:24px;height:24px;display:flex;align-items:center;"
                        f"justify-content:center;font-size:11px;font-weight:700;"
                        f"flex-shrink:0'>{flat_idx+1}</div>"
                        f"<div style='font-size:13px;font-weight:{'700' if is_done else '500'};"
                        f"color:{lbl_col};line-height:1.3'>"
                        f"{'✅ ' if is_done else ''}{topic}"
                        f"</div></div>",
                        unsafe_allow_html=True
                    )
                with mc2:
                    if st.button("Open", key=f"open_{ui}_{ti}",
                                 use_container_width=True, type="primary"):
                        st.session_state.syl_view           = "detail"
                        st.session_state.syl_topic_idx      = flat_idx
                        st.session_state.syl_detail_content = None
                        st.session_state.syl_detail_for     = None
                        st.rerun()
                with mc3:
                    mk_lbl = "✅" if is_done else "✓"
                    if st.button(mk_lbl, key=f"mk_{ui}_{ti}", use_container_width=True,
                                 help="Mark complete / incomplete"):
                        u = _toggle_done(u, syl_key, topic_key)
                        done_set = set(u.get("studied_topics", {}).get(syl_key, []))
                        st.rerun()


# ─────────────────────────────────────────────────────────────────
# PROGRESS PAGE
# ─────────────────────────────────────────────────────────────────
def page_progress():
    u     = st.session_state.user
    stats = u.get("stats",{})
    total = stats.get("total",0)

    st.markdown("<div class=\"section-header\">📊 My Progress</div>", unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("❓ Questions",  total)
    with c2: st.metric("🏆 Badges",     len(u.get("badges",[])))
    with c3: st.metric("🔥 Streak",     f"{stats.get('streak',0)} days")
    with c4: st.metric("🎯 Quizzes",    stats.get("quizzes_done",0))

    st.markdown("### 📚 Questions Per Subject")
    for name, info in SUBJECTS.items():
        cnt = stats.get(name,0)
        pct = int((cnt/max(total,1))*100)
        st.markdown(f"""
        <div style="margin-bottom:14px">
            <div style="display:flex;justify-content:space-between;font-size:13px;
                font-weight:700;margin-bottom:5px;color:#1A1A2E">
                <span>{info['emoji']} {name}</span>
                <span style="color:{info['color']}">{cnt} questions ({pct}%)</span>
            </div>
            <div class="prog-bar"><div class="prog-fill" style="width:{pct}%;background:{info['color']}"></div></div>
        </div>""", unsafe_allow_html=True)

    st.markdown("### 🛠️ Activity")
    c1,c2,c3 = st.columns(3)
    with c1: st.metric("🎨 Images Generated", stats.get("images",0))
    with c2: st.metric("📅 Member Since",      u.get("joined",""))
    with c3: st.metric("📖 Subjects Studied",  sum(1 for s in SUBJECTS if stats.get(s,0)>0))


# ─────────────────────────────────────────────────────────────────
# HISTORY PAGE
# FIX #4: Removed HTML-escaping of chat content before rendering
# with unsafe_allow_html. Instead use st.text for user messages
# and render bot messages safely. The original code escaped HTML
# but then rendered it, causing visible &lt; &gt; entities.
# ─────────────────────────────────────────────────────────────────
def page_history():
    u = st.session_state.user
    st.markdown("<div class=\"section-header\">🕐 Chat History</div>", unsafe_allow_html=True)
    hist     = load_json(HISTORY_FILE)
    sessions = sorted(hist.get(u["email"],[]), key=lambda x:x.get("updated",""), reverse=True)

    if not sessions:
        st.info("📭 No chat history yet. Start a conversation with Ustad!")
        return

    if not st.session_state.get("confirm_clear_hist"):
        if st.button("🗑️ Clear All History", type="secondary"):
            st.session_state.confirm_clear_hist = True; st.rerun()
    else:
        st.warning("⚠️ This will permanently delete all your chat history. Are you sure?")
        cc1, cc2 = st.columns(2)
        with cc1:
            if st.button("✅ Yes, delete all", type="primary", use_container_width=True):
                hist[u["email"]] = []
                save_json(HISTORY_FILE, hist)
                st.session_state.confirm_clear_hist = False
                st.success("History cleared."); st.rerun()
        with cc2:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.confirm_clear_hist = False; st.rerun()

    for sess in sessions:
        info  = SUBJECTS.get(sess.get("subject",""), {"emoji":"📚","color":"#666"})
        msgs  = sess.get("messages",[])
        label = (f"{info['emoji']} {sess.get('subject','')} — {sess.get('level','')} | "
                 f"{sess.get('updated','')} ({len(msgs)} msgs)")
        with st.expander(label):
            for m in msgs:
                if m["role"] == "user":
                    # FIX #4: Use st.text-like approach for user messages to avoid
                    # HTML injection while preserving styling
                    st.markdown(
                        f"<div class=\"msg-user\" style=\"margin-left:40px\">"
                        f"{m['content'].replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')}"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                else:
                    # Bot messages can contain markdown formatting — render as plain text
                    # to avoid XSS while preserving readability
                    st.markdown(
                        f"<div class=\"msg-bot\" style=\"margin-right:40px\">"
                        f"{m['content'].replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')}"
                        f"</div>",
                        unsafe_allow_html=True
                    )
            if st.button("🔄 Continue chat", key=f"cont_{sess['id']}"):
                st.session_state.chat_messages = msgs
                st.session_state.session_id    = sess["id"]
                st.session_state.subject       = sess.get("subject","Maths")
                st.session_state.page          = "chat"; st.rerun()


# ─────────────────────────────────────────────────────────────────
# BADGES PAGE
# ─────────────────────────────────────────────────────────────────
def page_badges():
    u      = st.session_state.user
    earned = u.get("badges",[])
    st.markdown("<div class=\"section-header orange\">🏆 Badges & Achievements</div>", unsafe_allow_html=True)
    st.markdown(f"<p style=\"color:#666;font-size:13px\">Earned "
                f"<b style=\"color:#1A1A2E\">{len(earned)}</b> of "
                f"<b style=\"color:#1A1A2E\">{len(BADGES)}</b> badges</p>", unsafe_allow_html=True)
    cols = st.columns(3)
    for i,b in enumerate(BADGES):
        is_earned = b["id"] in earned
        with cols[i%3]:
            locked = "" if is_earned else "badge-locked"
            status_color = "#059669" if is_earned else "#ccc"
            status_text  = "✅ Earned!" if is_earned else "🔒 Locked"
            st.markdown(f"""
            <div class="badge-card {locked}" style="margin-bottom:12px">
                <span class="badge-icon">{b['icon']}</span>
                <div class="badge-name">{b['name']}</div>
                <div class="badge-desc">{b['desc']}</div>
                <div style="font-size:11px;margin-top:5px;color:{status_color};font-weight:700">{status_text}</div>
            </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# PROFILE PAGE
# ─────────────────────────────────────────────────────────────────
def page_profile():
    u = st.session_state.user
    st.markdown("<div class=\"section-header\">👤 My Profile</div>", unsafe_allow_html=True)
    c1,c2 = st.columns([1,2])
    with c1:
        st.markdown(f"<div style=\"font-size:80px;text-align:center;background:#F3F4F6;"
                    f"border-radius:20px;padding:20px\">{u.get('avatar','👦')}</div>", unsafe_allow_html=True)
    with c2:
        role_label = (
            '🎒 Student'  if u.get('role')=='student'
            else '👨‍👩‍👦 Parent'  if u.get('role')=='parent'
            else '👨‍🏫 Teacher' if u.get('role')=='teacher'
            else '🛡️ Admin'    if u.get('role')=='admin'
            else '👤 User'
        )
        st.markdown(f"""
        <div style="padding:10px 0;color:#1A1A2E">
            <div style="font-size:22px;font-weight:800">{u['name']}</div>
            <div style="font-size:13px;color:#999;margin-top:4px">{role_label} • {u.get('grade','')}</div>
            <div style="font-size:12px;color:#bbb;margin-top:2px">📧 {u['email']}</div>
            <div style="font-size:12px;color:#bbb;margin-top:2px">📅 Joined {u.get('joined','')}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### ✏️ Update Profile")
    with st.form("profile_form"):
        new_name  = st.text_input("Full Name", value=u.get("name",""))
        new_grade = st.selectbox("Default Grade", ["-- Select --"]+LEVELS,
                                 index=get_level_index(u.get("grade","Grade 6"))+1)
        cur_av_key = next((k for k,v in AVATARS.items() if v==u.get("avatar","👦")), list(AVATARS.keys())[0])
        new_avatar = st.selectbox("Avatar", list(AVATARS.keys()),
                                  index=list(AVATARS.keys()).index(cur_av_key))
        st.markdown("#### 🔒 Change Password")
        old_pw = st.text_input("Current Password", type="password")
        new_pw = st.text_input("New Password", type="password", placeholder="Leave blank to keep current")
        cnf_pw = st.text_input("Confirm New Password", type="password")
        if st.form_submit_button("💾 Save Changes", type="primary"):
            users = load_json(USERS_FILE)
            eu    = users[u["email"]]
            if old_pw and eu["password"] != hash_pw(old_pw):
                st.error("Current password is incorrect.")
            elif new_pw and new_pw != cnf_pw:
                st.error("New passwords don't match.")
            elif new_pw and len(new_pw) < 6:
                st.error("Min 6 characters.")
            else:
                if new_name.strip():            eu["name"]   = new_name.strip()
                if new_grade != "-- Select --": eu["grade"]  = new_grade
                eu["avatar"] = AVATARS[new_avatar]
                if new_pw:                      eu["password"] = hash_pw(new_pw)
                users[u["email"]] = eu
                save_json(USERS_FILE, users)
                st.session_state.user = eu
                st.success("✅ Profile updated!"); time.sleep(0.5); st.rerun()


# ─────────────────────────────────────────────────────────────────
# HOMEWORK PAGE (Teacher / Admin)
# ─────────────────────────────────────────────────────────────────
def page_homework():
    u    = st.session_state.user
    role = u.get("role", "student")

    st.markdown("<div class=\"section-header\">📋 Homework Creator</div>", unsafe_allow_html=True)

    tab_create, tab_manage = st.tabs(["✏️  Create New", "📂  Manage Assignments"])

    # ══════════════════════════════════════════════════════
    # TAB 1 — CREATE
    # ══════════════════════════════════════════════════════
    with tab_create:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#EFF4FF,#F5F0FF);border-radius:14px;
            padding:14px 18px;margin-bottom:20px;font-size:13px;color:#1B4FD8;
            border-left:4px solid #2563EB">
            🤖 <b>AI Homework Generator</b> — Choose subject, topic, question types and difficulty.
            AI builds a complete assignment with questions, model answers, hints and a marking guide.
        </div>""", unsafe_allow_html=True)

        # ── Step 1: Subject & Grade ──────────────────────────
        st.markdown("#### 📚 Step 1 — Subject & Grade")
        c1, c2 = st.columns(2)
        with c1:
            hw_subject = st.selectbox("Subject", list(SUBJECTS.keys()), key="hw_subject")
        with c2:
            hw_grade = st.selectbox("Grade Level", LEVELS,
                                    index=get_level_index(u.get("grade", "Grade 6")),
                                    key="hw_grade")

        # Quick-pick topics from curriculum
        subj_key_map = {
            "Maths":"Maths","Physics":"Physics","Chemistry":"Chemistry",
            "Biology":"Biology","English":"English",
            "Computer Science":"Computer Science","Urdu":"Urdu",
        }
        curr_units = (CAMBRIDGE_CURRICULUM
                      .get(subj_key_map.get(hw_subject, "Maths"), {})
                      .get(hw_grade, {})
                      .get("units", []))

        # ── Step 2: Topic ───────────────────────────────────
        st.markdown("#### ✏️ Step 2 — Topic")

        if curr_units:
            with st.expander("📖 Quick-pick from Cambridge syllabus (optional)"):
                for unit in curr_units[:6]:
                    st.markdown(f"<div style='font-size:12px;font-weight:800;color:#2563EB;"
                                f"margin:6px 0 4px'>{unit['unit']}</div>",
                                unsafe_allow_html=True)
                    chip_cols = st.columns(3)
                    for ti, topic in enumerate(unit["topics"]):
                        with chip_cols[ti % 3]:
                            btn_key = f"tpick_{unit['unit'][:6]}_{ti}"
                            if st.button(topic, key=btn_key, use_container_width=True):
                                st.session_state["_hw_topic_pick"] = topic
                                st.rerun()

        picked = st.session_state.get("_hw_topic_pick", "")
        hw_topic = st.text_input(
            "Topic / Chapter",
            value=picked,
            placeholder="e.g. Quadratic Equations, Photosynthesis, Newton's Laws...",
            key="hw_topic_input"
        )
        if picked:
            st.caption(f"📌 Picked from syllabus: **{picked}** — edit above if needed")

        hw_context = st.text_area(
            "Additional Instructions (optional)",
            placeholder="e.g. Focus on diagrams. Include a real-life word problem. Time limit: 30 min...",
            height=75, key="hw_context"
        )

        # ── Step 3: Homework Type ───────────────────────────
        st.markdown("#### 📝 Step 3 — Homework Type")

        HW_TYPES = {
            "Mixed (MCQ + Short + Long)":  ("🎯","#2563EB","Balanced: multiple types in one assignment"),
            "MCQ Only":                    ("🔵","#0891B2","Multiple choice — easy to auto-mark"),
            "Short Answer":                ("📝","#059669","Brief written answers — tests understanding"),
            "Long Answer / Essay":         ("📄","#7C3AED","Extended writing — analytical skills"),
            "Problem Solving":             ("🔢","#E8472A","Step-by-step worked problems — Maths/Science"),
            "Fill in the Blanks":          ("📑","#D97706","Key-term completion — great for vocabulary"),
            "True / False + Justify":      ("✅","#0D6E3F","Critical thinking — justify each answer"),
            "Research & Summary":          ("🔍","#BE185D","Read and summarise — builds study skills"),
            "Diagram & Label":             ("🗺️","#6D28D9","Draw, label or interpret diagrams"),
            "Past Paper Style":            ("🏆","#B45309","Exam-format questions following board style"),
        }

        col_t1, col_t2 = st.columns(2)
        hw_type_list = list(HW_TYPES.keys())
        with col_t1:
            hw_type = st.selectbox("Question Type", hw_type_list, key="hw_type")
        t_icon, t_color, t_desc = HW_TYPES[hw_type]
        with col_t2:
            st.markdown(f"""
            <div style="background:{t_color}12;border-radius:10px;padding:10px 14px;
                font-size:12px;color:{t_color};border-left:3px solid {t_color};margin-top:28px">
                {t_icon} <b>{hw_type}:</b> {t_desc}
            </div>""", unsafe_allow_html=True)

        # ── Step 4: Settings ────────────────────────────────
        st.markdown("#### ⚙️ Step 4 — Question Settings")
        c3, c4, c5, c6 = st.columns(4)
        with c3:
            hw_difficulty  = st.selectbox("Difficulty", ["Easy","Medium","Hard","Mixed"], index=1, key="hw_diff")
        with c4:
            hw_num_q       = st.selectbox("No. of Questions", [3,5,8,10,12,15], index=1, key="hw_num_q")
        with c5:
            hw_marks_each  = st.selectbox("Marks Each", [1,2,3,5], index=1, key="hw_marks")
        with c6:
            hw_due_days    = st.selectbox("Due In", [1,2,3,5,7,10,14,21],
                                          index=2, format_func=lambda x: f"{x} day{'s' if x!=1 else ''}",
                                          key="hw_due_days")

        due_date          = (datetime.date.today() + datetime.timedelta(days=hw_due_days)).isoformat()
        total_marks_prev  = hw_num_q * hw_marks_each
        est_mins          = hw_num_q * (3 if hw_difficulty=="Easy" else 5 if hw_difficulty=="Medium" else 7)

        st.markdown(f"""
        <div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:8px">
            <span style="background:#EFF4FF;color:#1B4FD8;padding:5px 14px;border-radius:99px;
                font-size:12px;font-weight:700">📊 Total: {total_marks_prev} marks</span>
            <span style="background:#F0FDF4;color:#065F46;padding:5px 14px;border-radius:99px;
                font-size:12px;font-weight:700">⏱️ ~{est_mins} minutes</span>
            <span style="background:#FFF8E7;color:#92400E;padding:5px 14px;border-radius:99px;
                font-size:12px;font-weight:700">📅 Due: {due_date}</span>
        </div>""", unsafe_allow_html=True)

        # Options row
        oc1, oc2, oc3 = st.columns(3)
        with oc1: hw_hints    = st.checkbox("Include hints",             value=True,  key="hw_hints")
        with oc2: hw_show_ans = st.checkbox("Show answers after submit", value=True,  key="hw_show_ans")
        with oc3: hw_obj      = st.checkbox("Learning objectives",       value=True,  key="hw_obj")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # ── Generate ────────────────────────────────────────
        if st.button("🚀 Generate Homework with AI", use_container_width=True,
                     type="primary", key="gen_hw_btn"):
            topic_str = hw_topic.strip()
            if not topic_str:
                st.error("⚠️ Please enter a topic in Step 2.")
            else:
                type_instruction = {
                    "MCQ Only":
                        f"ALL {hw_num_q} questions MUST be MCQ type with exactly 4 options each.",
                    "Short Answer":
                        f"ALL {hw_num_q} questions MUST be short_answer type (2–3 sentences).",
                    "Long Answer / Essay":
                        f"ALL {hw_num_q} questions MUST be long_answer type (paragraph response).",
                    "Problem Solving":
                        f"ALL {hw_num_q} questions MUST be problem type with step-by-step solution.",
                    "Fill in the Blanks":
                        f"ALL {hw_num_q} questions MUST be short_answer fill-in-the-blank style.",
                    "True / False + Justify":
                        f"ALL {hw_num_q} questions MUST be short_answer true/false with justification.",
                    "Research & Summary":
                        f"ALL {hw_num_q} tasks MUST be long_answer research/summary style.",
                    "Diagram & Label":
                        f"ALL {hw_num_q} questions MUST be short_answer asking students to label/describe diagrams.",
                    "Past Paper Style":
                        f"Generate {hw_num_q} exam-style questions following Cambridge/FBISE format.",
                    "Mixed (MCQ + Short + Long)":
                        f"Generate a MIX: roughly {hw_num_q//3} MCQ, {hw_num_q//3} short_answer, "
                        f"{hw_num_q - 2*(hw_num_q//3)} long_answer.",
                }.get(hw_type, f"Generate {hw_num_q} questions.")

                ctx_part = f" Additional context: {hw_context.strip()}." if hw_context.strip() else ""
                hint_part = " Include a helpful hint for every question." if hw_hints else ""
                obj_part  = " Include clear learning objectives." if hw_obj else ""

                prompt = (
                    f"Create a complete homework assignment for {hw_grade} {hw_subject} students in Pakistan.\n"
                    f"Topic: {topic_str}.{ctx_part}\n"
                    f"Homework type: {hw_type}. {type_instruction}\n"
                    f"Difficulty: {hw_difficulty}. Each question is worth {hw_marks_each} mark(s).\n"
                    f"{hint_part}{obj_part}\n"
                    f"Return ONLY raw JSON (no markdown, no backticks):\n"
                    f'{{"title":"homework title",'
                    f'"instructions":"clear student instructions",'
                    f'"learning_objectives":"what students will learn",'
                    f'"estimated_time":"{est_mins} minutes",'
                    f'"questions":[{{'
                    f'"number":1,'
                    f'"type":"MCQ|short_answer|long_answer|problem",'
                    f'"question":"question text",'
                    f'"marks":{hw_marks_each},'
                    f'"options":["A. ...","B. ...","C. ...","D. ..."],'
                    f'"answer":"correct answer or full model answer",'
                    f'"hint":"helpful hint without giving away the answer",'
                    f'"explanation":"why this answer is correct"'
                    f'}}],'
                    f'"total_marks":{total_marks_prev},'
                    f'"marking_guide":"concise marking guidance"}}'
                )

                hw_tokens = max(2500, hw_num_q * 350 + 800)
                with st.spinner(f"✨ Generating {hw_num_q} {hw_difficulty} questions on '{topic_str}'…"):
                    raw = call_ai(
                        [{"role":"user","content": prompt}],
                        "Expert Pakistani curriculum homework generator. Return ONLY valid JSON, no extra text.",
                        hw_tokens
                    )

                if raw.startswith(("__API_KEY_MISSING__","__EMPTY_RESPONSE__","__API_ERROR__:")):
                    st.error(f"⚠️ AI error: {raw}")
                else:
                    try:
                        clean = raw.strip()
                        for fence in ["```json","```"]:
                            clean = clean.replace(fence,"")
                        clean = clean.strip()
                        j0 = clean.find("{"); j1 = clean.rfind("}") + 1
                        if j0 >= 0 and j1 > j0:
                            clean = clean[j0:j1]
                        hw_data = json.loads(clean)
                        questions = hw_data.get("questions",[])
                        if not questions:
                            raise ValueError("No questions in AI response")

                        homework = load_json(HOMEWORK_FILE)
                        hw_id    = (f"hw_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_"
                                    f"{u['email'].split('@')[0]}")
                        homework[hw_id] = {
                            "id":           hw_id,
                            "created_by":   u["email"],
                            "creator_name": u["name"],
                            "creator_role": role,
                            "subject":      hw_subject,
                            "grade":        hw_grade,
                            "topic":        topic_str,
                            "type":         hw_type,
                            "difficulty":   hw_difficulty,
                            "due_date":     due_date,
                            "created":      datetime.date.today().isoformat(),
                            "status":       "active",
                            "show_hints":   hw_hints,
                            "show_answers": hw_show_ans,
                            "submissions":  {},
                            "data":         hw_data,
                        }
                        save_json(HOMEWORK_FILE, homework)
                        st.session_state["hw_preview_id"] = hw_id
                        st.session_state["_hw_topic_pick"] = ""
                        st.success("✅ Homework generated and saved!")
                        st.balloons()
                        st.rerun()
                    except Exception as e:
                        st.error(f"⚠️ Could not parse AI response: {e}")
                        with st.expander("🔍 Debug — AI raw output"):
                            st.code(raw[:1000])

        # ── Preview ─────────────────────────────────────────
        prev_id = st.session_state.get("hw_preview_id")
        if prev_id:
            hw_all  = load_json(HOMEWORK_FILE)
            hw_prev = hw_all.get(prev_id)
            if hw_prev:
                _render_hw_card(hw_prev, show_answers=True, creator_view=True)

    # ══════════════════════════════════════════════════════
    # TAB 2 — MANAGE
    # ══════════════════════════════════════════════════════
    with tab_manage:
        homework = load_json(HOMEWORK_FILE)
        if role == "admin":
            my_hw = list(homework.values())
        else:
            my_hw = [h for h in homework.values()
                     if h.get("created_by") == u["email"]]

        if not my_hw:
            st.info("📭 No assignments yet. Use the 'Create New' tab to get started!")
        else:
            total_subs = sum(len(h.get("submissions",{})) for h in my_hw)
            avg_all    = 0
            sub_scores = []
            for h in my_hw:
                for s in h.get("submissions",{}).values():
                    sub_scores.append(s.get("score_pct",0))
            if sub_scores:
                avg_all = int(sum(sub_scores)/len(sub_scores))

            ma, mb, mc = st.columns(3)
            for col, icon, val, lbl, col_c in [
                (ma,"📋",len(my_hw),  "Assignments","#2563EB"),
                (mb,"📬",total_subs,  "Submissions", "#7C3AED"),
                (mc,"📈",f"{avg_all}%","Avg Score",  "#059669"),
            ]:
                with col:
                    st.markdown(f"""
                    <div style="background:#fff;border-radius:12px;padding:14px;text-align:center;
                        box-shadow:0 2px 10px rgba(0,0,0,.06);border-top:4px solid {col_c}">
                        <div style="font-size:22px">{icon}</div>
                        <div style="font-size:22px;font-weight:900;color:{col_c}">{val}</div>
                        <div style="font-size:11px;color:#999;font-weight:700">{lbl}</div>
                    </div>""", unsafe_allow_html=True)

            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            f1, f2, f3 = st.columns(3)
            with f1: f_sub  = st.selectbox("Subject",["All"]+list(SUBJECTS.keys()), key="mng_fsub")
            with f2: f_stat = st.selectbox("Status", ["All","Active","Inactive"],    key="mng_fstat")
            with f3: f_sort = st.selectbox("Sort by",["Newest","Oldest","Subject"],  key="mng_fsort")

            filtered = [
                h for h in my_hw
                if (f_sub=="All" or h.get("subject")==f_sub)
                and (f_stat=="All"
                     or (f_stat=="Active"   and h.get("status","active")=="active")
                     or (f_stat=="Inactive" and h.get("status","active")!="active"))
            ]
            if f_sort=="Newest":   filtered.sort(key=lambda x:x.get("created",""), reverse=True)
            elif f_sort=="Oldest": filtered.sort(key=lambda x:x.get("created",""))
            else:                  filtered.sort(key=lambda x:x.get("subject",""))

            for hw in filtered:
                info      = SUBJECTS.get(hw.get("subject","Maths"), {"emoji":"📚","color":"#2563EB"})
                col_c     = info["color"]
                subs      = hw.get("submissions",{})
                sub_cnt   = len(subs)
                data      = hw.get("data",{})
                hw_title  = data.get("title", hw.get("topic","Homework"))
                due       = hw.get("due_date","")
                overdue   = due < datetime.date.today().isoformat() if due else False
                is_active = hw.get("status","active") == "active"
                scores    = [s.get("score_pct",0) for s in subs.values()]
                avg_sc    = int(sum(scores)/len(scores)) if scores else 0
                hi = sum(1 for s in scores if s>=80)
                lo = sum(1 for s in scores if s<60)

                due_bg  = "#FEE2E2" if overdue else "#D1FAE5"
                due_col = "#991B1B" if overdue else "#065F46"
                due_lbl = f"⚠️ Overdue" if overdue else f"📅 Due {due}"

                with st.expander(
                    f"{info['emoji']} {hw_title[:48]}{'…' if len(hw_title)>48 else ''} "
                    f"| {hw.get('grade','')} | {'🟢' if is_active else '🔴'} "
                    f"| {sub_cnt} sub(s) | Avg {avg_sc}%"
                ):
                    st.markdown(f"""
                    <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px">
                        <span style="background:{col_c}18;color:{col_c};padding:3px 12px;
                            border-radius:99px;font-size:12px;font-weight:700">
                            {info['emoji']} {hw.get('subject','')}</span>
                        <span style="background:{col_c}18;color:{col_c};padding:3px 12px;
                            border-radius:99px;font-size:12px;font-weight:700">
                            🏫 {hw.get('grade','')}</span>
                        <span style="background:#F3F4F6;color:#374151;padding:3px 12px;
                            border-radius:99px;font-size:12px;font-weight:700">
                            📝 {hw.get('type','')}</span>
                        <span style="background:{col_c}18;color:{col_c};padding:3px 12px;
                            border-radius:99px;font-size:12px;font-weight:700">
                            🎯 {hw.get('difficulty','')}</span>
                        <span style="background:{due_bg};color:{due_col};padding:3px 12px;
                            border-radius:99px;font-size:12px;font-weight:700">{due_lbl}</span>
                    </div>""", unsafe_allow_html=True)

                    if sub_cnt > 0:
                        sc1,sc2,sc3,sc4 = st.columns(4)
                        with sc1: st.metric("📬 Submitted", sub_cnt)
                        with sc2: st.metric("📈 Avg Score", f"{avg_sc}%")
                        with sc3: st.metric("🏆 High ≥80%", hi)
                        with sc4: st.metric("⚠️ Low <60%",  lo)
                        st.markdown("**Students:**")
                        for em, sub in sorted(subs.items(),
                                              key=lambda x:x[1].get("score_pct",0), reverse=True):
                            sp  = sub.get("score_pct",0)
                            dot = "🟢" if sp>=80 else "🟡" if sp>=60 else "🔴"
                            st.markdown(f"""
                            <div style="background:#F8F9FA;border-radius:8px;padding:7px 14px;
                                margin-bottom:3px;display:flex;justify-content:space-between">
                                <span style="font-size:13px;font-weight:700">{dot} {sub.get('student_name',em)}</span>
                                <span style="font-size:12px;color:#666">
                                    {sub.get('score',0)}/{sub.get('total_marks',0)} ({sp}%)
                                    · {sub.get('submitted_at','')}</span>
                            </div>""", unsafe_allow_html=True)
                    else:
                        st.info("No submissions yet.")

                    ba, bb, bc = st.columns(3)
                    with ba:
                        lbl_toggle = "🔴 Deactivate" if is_active else "🟢 Activate"
                        if st.button(lbl_toggle, key=f"tog_{hw['id']}", use_container_width=True):
                            hw_fresh = load_json(HOMEWORK_FILE)
                            if hw["id"] in hw_fresh:
                                hw_fresh[hw["id"]]["status"] = "inactive" if is_active else "active"
                                save_json(HOMEWORK_FILE, hw_fresh)
                            st.rerun()
                    with bb:
                        if st.button("👁️ Preview", key=f"prv_{hw['id']}", use_container_width=True):
                            st.session_state["hw_preview_id"] = hw["id"]
                            st.rerun()
                    with bc:
                        if st.button("🗑️ Delete", key=f"del_{hw['id']}", use_container_width=True):
                            hw_fresh = load_json(HOMEWORK_FILE)
                            hw_fresh.pop(hw["id"], None)
                            save_json(HOMEWORK_FILE, hw_fresh)
                            if st.session_state.get("hw_preview_id") == hw["id"]:
                                st.session_state["hw_preview_id"] = None
                            st.rerun()



def _render_hw_card(hw_prev, show_answers=True, creator_view=False):
    """Shared renderer: homework preview card with all questions, answers, hints."""
    data   = hw_prev.get("data", {})
    info   = SUBJECTS.get(hw_prev.get("subject","Maths"), {"emoji":"📚","color":"#2563EB"})
    col_c  = info["color"]
    qs     = data.get("questions", [])

    st.markdown("---")
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{col_c}14,{col_c}06);
        border:2px solid {col_c}40;border-radius:18px;padding:20px 22px;margin-bottom:16px">
        <div style="font-size:20px;font-weight:900;color:#1A1A2E;margin-bottom:10px">
            {info['emoji']} {data.get('title', hw_prev.get('topic','Homework'))}
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px">
            <span style="background:{col_c}20;color:{col_c};padding:3px 12px;
                border-radius:99px;font-size:12px;font-weight:700">
                📚 {hw_prev.get('subject','')}</span>
            <span style="background:{col_c}20;color:{col_c};padding:3px 12px;
                border-radius:99px;font-size:12px;font-weight:700">
                🏫 {hw_prev.get('grade','')}</span>
            <span style="background:{col_c}20;color:{col_c};padding:3px 12px;
                border-radius:99px;font-size:12px;font-weight:700">
                🎯 {hw_prev.get('difficulty','')}</span>
            <span style="background:{col_c}20;color:{col_c};padding:3px 12px;
                border-radius:99px;font-size:12px;font-weight:700">
                📝 {len(qs)} questions · {data.get('total_marks',0)} marks</span>
            <span style="background:#D1FAE5;color:#065F46;padding:3px 12px;
                border-radius:99px;font-size:12px;font-weight:700">
                📅 Due: {hw_prev.get('due_date','')}</span>
            <span style="background:#FFF8E7;color:#92400E;padding:3px 12px;
                border-radius:99px;font-size:12px;font-weight:700">
                ⏱️ {data.get('estimated_time','')}</span>
        </div>
        <div style="font-size:13px;color:#374151;margin-bottom:6px;line-height:1.6">
            <b>📋 Instructions:</b> {data.get('instructions','')[:300]}
        </div>
        <div style="font-size:12px;color:#6B7280;line-height:1.5">
            <b>🎯 Learning Objectives:</b> {data.get('learning_objectives','')}
        </div>
    </div>""", unsafe_allow_html=True)

    TYPE_META = {
        "MCQ":          ("🔵","#2563EB","Multiple Choice"),
        "short_answer": ("📝","#059669","Short Answer"),
        "long_answer":  ("📄","#7C3AED","Long Answer"),
        "problem":      ("🔢","#E8472A","Problem"),
    }

    st.markdown(f"#### 📝 Questions ({len(qs)} total)")
    for i, q in enumerate(qs):
        t_icon, t_col, t_lbl = TYPE_META.get(q.get("type",""), ("❓","#666","Question"))
        marks = q.get("marks",1)
        marks_lbl = f"{marks} mark{'s' if marks!=1 else ''}"

        with st.expander(
            f"Q{i+1}. {q['question'][:72]}{'…' if len(q['question'])>72 else ''} [{marks_lbl}]"
        ):
            st.markdown(f"""
            <span style="background:{t_col}18;color:{t_col};padding:3px 12px;
                border-radius:99px;font-size:12px;font-weight:700;
                display:inline-block;margin-bottom:10px">
                {t_icon} {t_lbl} · {marks_lbl}
            </span>
            <div style="font-size:14px;font-weight:700;color:#1A1A2E;
                line-height:1.55;margin-bottom:10px">{q['question']}</div>
            """, unsafe_allow_html=True)

            if q.get("options"):
                for opt in q["options"]:
                    st.markdown(f"""
                    <div style="background:#F8F9FA;border-radius:8px;padding:7px 12px;
                        margin-bottom:4px;font-size:13px;color:#374151">{opt}</div>
                    """, unsafe_allow_html=True)

            if show_answers:
                r1, r2 = st.columns(2)
                with r1:
                    st.markdown(f"""
                    <div style="background:#D1FAE5;border-radius:8px;padding:8px 12px;
                        margin-top:6px;font-size:12px;color:#065F46">
                        ✅ <b>Answer:</b> {q.get('answer','')}
                    </div>""", unsafe_allow_html=True)
                with r2:
                    if q.get("hint"):
                        st.markdown(f"""
                        <div style="background:#FFF8E7;border-radius:8px;padding:8px 12px;
                            margin-top:6px;font-size:12px;color:#92400E">
                            💡 <b>Hint:</b> {q.get('hint','')}
                        </div>""", unsafe_allow_html=True)
                if q.get("explanation"):
                    st.markdown(f"""
                    <div style="background:#F3F4FF;border-radius:8px;padding:8px 12px;
                        margin-top:4px;font-size:12px;color:#3730A3">
                        📖 <b>Explanation:</b> {q.get('explanation','')}
                    </div>""", unsafe_allow_html=True)

    if data.get("marking_guide"):
        st.markdown(f"""
        <div style="background:#FFF8E7;border:1.5px solid #F5CC4A;border-radius:12px;
            padding:14px 16px;margin-top:14px">
            <div style="font-size:13px;font-weight:800;color:#92400E;margin-bottom:6px">
                📖 Marking Guide</div>
            <div style="font-size:13px;color:#78350F;line-height:1.6">
                {data.get('marking_guide','')}</div>
        </div>""", unsafe_allow_html=True)

    if creator_view:
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        ba, bb = st.columns(2)
        with ba:
            if st.button("➕ Create Another", use_container_width=True,
                         type="primary", key="hw_create_another"):
                st.session_state["hw_preview_id"] = None
                st.rerun()
        with bb:
            if st.button("📂 Clear Preview", use_container_width=True, key="hw_clear_prev"):
                st.session_state["hw_preview_id"] = None
                st.rerun()




# ─────────────────────────────────────────────────────────────────
# ADMIN DASHBOARD
# ─────────────────────────────────────────────────────────────────
def page_admin():
    st.markdown("<div class=\"section-header orange\">🛡️ Admin Dashboard</div>", unsafe_allow_html=True)

    users    = load_json(USERS_FILE)
    homework = load_json(HOMEWORK_FILE)

    students  = {e: d for e, d in users.items() if d.get("role") not in ("admin",)}
    all_hw    = list(homework.values())

    tab_perf, tab_hw = st.tabs([
        "📊 Student Performance Analytics",
        "📋 Homework Tracking",
    ])

    with tab_perf:
        st.markdown("### 📊 Platform Overview")
        total_students  = len(students)
        total_questions = sum(d.get("stats",{}).get("total",0)        for d in students.values())
        total_quizzes   = sum(d.get("stats",{}).get("quizzes_done",0) for d in students.values())
        avg_streak      = (sum(d.get("stats",{}).get("streak",0) for d in students.values())
                           / max(total_students, 1))

        c1, c2, c3, c4 = st.columns(4)
        for col_w, icon, val, lbl, color in [
            (c1, "🎒", total_students,       "Total Users",      "#2563EB"),
            (c2, "❓", total_questions,      "Questions Asked",  "#E8472A"),
            (c3, "📝", total_quizzes,        "Quizzes Done",     "#7C3AED"),
            (c4, "🔥", f"{avg_streak:.1f}d", "Avg Streak",       "#F59E0B"),
        ]:
            with col_w:
                st.markdown(f"""
                <div style="background:#fff;border-radius:14px;padding:18px 14px;text-align:center;
                    box-shadow:0 2px 12px rgba(0,0,0,0.07);border-top:4px solid {color}">
                    <div style="font-size:26px">{icon}</div>
                    <div style="font-size:26px;font-weight:900;color:{color};margin:4px 0">{val}</div>
                    <div style="font-size:11px;color:#999;font-weight:700">{lbl}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("### 🏆 Top 10 Students — Engagement Leaderboard")

        sorted_users = sorted(
            students.items(),
            key=lambda x: (
                x[1].get("stats",{}).get("total",0)
                + x[1].get("stats",{}).get("quizzes_done",0) * 3
                + x[1].get("stats",{}).get("streak",0) * 2
                + len(x[1].get("badges",[])) * 5
            ),
            reverse=True
        )

        rank_icons = ["🥇","🥈","🥉"] + [f"{i+1}️⃣" for i in range(3,10)]
        max_score  = max(
            (s.get("stats",{}).get("total",0)
             + s.get("stats",{}).get("quizzes_done",0)*3
             + s.get("stats",{}).get("streak",0)*2
             + len(s.get("badges",[]))*5
             for _,s in sorted_users[:1]),
            default=1
        )

        for i, (email, ud) in enumerate(sorted_users[:10]):
            stats   = ud.get("stats", {})
            qs      = stats.get("total", 0)
            quizzes = stats.get("quizzes_done", 0)
            streak  = stats.get("streak", 0)
            badges  = len(ud.get("badges", []))
            score   = qs + quizzes*3 + streak*2 + badges*5
            bar_pct = min(int((score / max(max_score, 1)) * 100), 100)
            bar_col = "#FFD700" if i < 3 else "#6366F1"
            top_subj = max(
                [(s, stats.get(s,0)) for s in SUBJECTS],
                key=lambda x: x[1], default=("—", 0)
            )
            grade = ud.get("grade","")

            st.markdown(f"""
            <div style="background:#fff;border-radius:14px;padding:14px 18px;
                margin-bottom:10px;box-shadow:0 2px 10px rgba(0,0,0,0.06);
                border-left:5px solid {"#FFD700" if i<3 else "#E0E7FF"};color:#1A1A2E">
                <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px">
                    <div style="display:flex;align-items:center;gap:12px">
                        <span style="font-size:24px">{rank_icons[i]}</span>
                        <div>
                            <div style="font-weight:800;font-size:15px">
                                {ud.get("avatar","👤")} {ud.get("name","?")}
                            </div>
                            <div style="font-size:11px;color:#aaa">{grade} &nbsp;·&nbsp; {email}</div>
                        </div>
                    </div>
                    <div style="display:flex;gap:18px;font-size:12px;flex-wrap:wrap">
                        <div style="text-align:center">
                            <div style="font-weight:900;font-size:17px;color:#E8472A">{qs}</div>
                            <div style="color:#bbb">Qs</div>
                        </div>
                        <div style="text-align:center">
                            <div style="font-weight:900;font-size:17px;color:#2563EB">{quizzes}</div>
                            <div style="color:#bbb">Quizzes</div>
                        </div>
                        <div style="text-align:center">
                            <div style="font-weight:900;font-size:17px;color:#F59E0B">{streak}d</div>
                            <div style="color:#bbb">Streak</div>
                        </div>
                        <div style="text-align:center">
                            <div style="font-weight:900;font-size:17px;color:#7C3AED">{badges}</div>
                            <div style="color:#bbb">Badges</div>
                        </div>
                    </div>
                </div>
                <div style="margin-top:10px">
                    <div style="display:flex;justify-content:space-between;
                        font-size:11px;color:#bbb;margin-bottom:4px">
                        <span>🏅 Top subject: {SUBJECTS.get(top_subj[0],{}).get("emoji","")}&nbsp;{top_subj[0]} ({top_subj[1]} Qs)</span>
                        <span style="font-weight:700;color:{bar_col}">Score: {score}</span>
                    </div>
                    <div style="background:#F0F0F8;border-radius:99px;height:10px;overflow:hidden">
                        <div style="width:{bar_pct}%;height:10px;border-radius:99px;
                            background:linear-gradient(90deg,{bar_col},{bar_col}88);
                            transition:width 1s ease"></div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

        if not sorted_users:
            st.info("No user data available yet.")

        st.markdown("### 📚 Platform-Wide Subject Engagement")
        subject_totals = {
            s: sum(d.get("stats",{}).get(s,0) for d in students.values())
            for s in SUBJECTS
        }
        grand_total = max(sum(subject_totals.values()), 1)

        for subj, count in sorted(subject_totals.items(), key=lambda x: x[1], reverse=True):
            info    = SUBJECTS[subj]
            pct     = int((count / grand_total) * 100)
            bar_w   = max(pct, 2)
            st.markdown(f"""
            <div style="margin-bottom:14px">
                <div style="display:flex;justify-content:space-between;
                    font-size:13px;font-weight:700;margin-bottom:5px;color:#1A1A2E">
                    <span>{info["emoji"]} {subj}</span>
                    <span style="color:{info["color"]}">{count} questions &nbsp;·&nbsp; {pct}%</span>
                </div>
                <div style="background:#F0F0F8;border-radius:99px;height:12px;overflow:hidden">
                    <div style="width:{bar_w}%;height:12px;border-radius:99px;
                        background:linear-gradient(90deg,{info["color"]},{info["color"]}88);
                        transition:width 1s ease"></div>
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("### 🗓️ 7-Day Activity Heatmap")
        today = datetime.date.today()
        days  = [(today - datetime.timedelta(days=i)) for i in range(6, -1, -1)]
        activity = {d.isoformat(): 0 for d in days}
        for ud in students.values():
            study_dates_list = ud.get("stats", {}).get("study_dates", [])
            for d_iso in study_dates_list:
                if d_iso in activity:
                    activity[d_iso] += 1
            if not study_dates_list:
                last = ud.get("stats", {}).get("lastDate", "")
                if last in activity:
                    activity[last] += 1

        max_act = max(max(activity.values(), default=0), 1)
        for day_iso, cnt in activity.items():
            day_obj  = datetime.date.fromisoformat(day_iso)
            weekday  = day_obj.strftime("%a %d %b")
            bar_w    = max(int((cnt / max_act) * 100), 2) if cnt else 0
            is_today = day_iso == today.isoformat()
            bar_col  = "#E8472A" if is_today else "#2563EB"
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
                <div style="font-size:12px;color:{"#E8472A" if is_today else "#888"};
                    font-weight:{"800" if is_today else "400"};width:90px;flex-shrink:0">
                    {"📍 " if is_today else ""}{weekday}
                </div>
                <div style="flex:1;background:#F0F0F8;border-radius:99px;height:20px;overflow:hidden">
                    <div style="width:{bar_w}%;height:20px;border-radius:99px;
                        background:linear-gradient(90deg,{bar_col},{bar_col}88)"></div>
                </div>
                <div style="font-size:13px;font-weight:800;color:#1A1A2E;width:28px;text-align:right">
                    {cnt}
                </div>
            </div>""", unsafe_allow_html=True)

    with tab_hw:
        st.markdown("### 📋 Homework Tracking")

        if not all_hw:
            st.info("📭 No homework assignments have been created yet.")
        else:
            total_hw   = len(all_hw)
            total_subs = sum(len(h.get("submissions", {})) for h in all_hw)
            est_poss   = total_hw * max(len(students), 1)
            comp_pct   = min(int((total_subs / max(est_poss, 1)) * 100), 100)
            comp_color = "#059669" if comp_pct >= 70 else "#F59E0B" if comp_pct >= 40 else "#E8472A"

            c1, c2, c3 = st.columns(3)
            for col_w, icon, val, lbl, color in [
                (c1, "📋", total_hw,   "Assignments",      "#2563EB"),
                (c2, "📬", total_subs, "Total Submissions","#7C3AED"),
                (c3, "📈", f"{comp_pct}%", "Est. Completion", comp_color),
            ]:
                with col_w:
                    st.markdown(f"""
                    <div style="background:#fff;border-radius:14px;padding:16px;text-align:center;
                        box-shadow:0 2px 10px rgba(0,0,0,0.06);border-top:4px solid {color}">
                        <div style="font-size:22px">{icon}</div>
                        <div style="font-size:24px;font-weight:900;color:{color}">{val}</div>
                        <div style="font-size:11px;color:#999;font-weight:700">{lbl}</div>
                    </div>""", unsafe_allow_html=True)

            f1, f2 = st.columns(2)
            with f1:
                f_subj   = st.selectbox("Subject", ["All"] + list(SUBJECTS.keys()), key="adm_f_subj")
            with f2:
                f_status = st.selectbox("Status",  ["All", "Active", "Inactive"],   key="adm_f_status")

            st.markdown("---")

            for hw in sorted(all_hw, key=lambda x: x.get("created",""), reverse=True):
                if f_subj != "All" and hw.get("subject") != f_subj:
                    continue
                hw_active = hw.get("status","active") == "active"
                if f_status == "Active"   and not hw_active: continue
                if f_status == "Inactive" and hw_active:     continue

                info      = SUBJECTS.get(hw["subject"], {"emoji":"📚","color":"#2563EB"})
                col_c     = info["color"]
                subs      = hw.get("submissions", {})
                sub_cnt   = len(subs)
                data      = hw.get("data", {})
                hw_title  = data.get("title", hw.get("topic",""))
                due       = hw.get("due_date","")
                today_str = datetime.date.today().isoformat()
                overdue   = due < today_str if due else False

                if subs:
                    scores    = [s.get("score_pct",0) for s in subs.values()]
                    avg_score = int(sum(scores) / len(scores))
                    high_q    = sum(1 for s in scores if s >= 80)
                    mid_q     = sum(1 for s in scores if 60 <= s < 80)
                    low_q     = sum(1 for s in scores if s < 60)
                    q_label   = "🟢 High" if avg_score>=80 else "🟡 Medium" if avg_score>=60 else "🔴 Low"
                else:
                    avg_score = high_q = mid_q = low_q = 0
                    q_label   = "⚪ No data"

                status_badge = "🟢 Active" if hw_active else "🔴 Inactive"
                due_label    = (f"⚠️ Overdue ({due})" if overdue else f"📅 Due: {due}")

                with st.expander(
                    f"{info['emoji']} {hw_title[:45]}{'…' if len(hw_title)>45 else ''} "
                    f"| {hw.get('subject','')} {hw.get('grade','')} "
                    f"| {status_badge} | {sub_cnt} sub(s) | Avg: {avg_score}%"
                ):
                    st.markdown(f"""
                    <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px">
                        <span style="background:{col_c}18;color:{col_c};padding:3px 10px;
                            border-radius:99px;font-size:12px;font-weight:700">{info["emoji"]} {hw["subject"]}</span>
                        <span style="background:{col_c}18;color:{col_c};padding:3px 10px;
                            border-radius:99px;font-size:12px;font-weight:700">🏫 {hw.get("grade","")}</span>
                        <span style="background:{col_c}18;color:{col_c};padding:3px 10px;
                            border-radius:99px;font-size:12px;font-weight:700">🎯 {hw.get("difficulty","")}</span>
                        <span style="background:{"#FEE2E2" if overdue else "#D1FAE5"};
                            color:{"#991B1B" if overdue else "#065F46"};padding:3px 10px;
                            border-radius:99px;font-size:12px;font-weight:700">{due_label}</span>
                    </div>""", unsafe_allow_html=True)

                    if sub_cnt > 0:
                        m1, m2, m3 = st.columns(3)
                        with m1: st.metric("📬 Submissions", sub_cnt)
                        with m2: st.metric("📈 Avg Score",  f"{avg_score}%")
                        with m3: st.metric("🏅 Quality",    q_label)

                        for email_s, sub in sorted(
                            subs.items(),
                            key=lambda x: x[1].get("score_pct",0),
                            reverse=True
                        ):
                            sp       = sub.get("score_pct", 0)
                            q_dot    = "🟢" if sp>=80 else "🟡" if sp>=60 else "🔴"
                            sub_time = sub.get("submitted_at","")
                            st.markdown(f"""
                            <div style="background:#F8F9FA;border-radius:10px;padding:9px 14px;
                                margin-bottom:5px;border-left:3px solid {col_c};color:#1A1A2E;
                                display:flex;justify-content:space-between;
                                align-items:center;flex-wrap:wrap;gap:6px">
                                <div>
                                    <b>{sub.get("student_name","?")}</b>
                                    <span style="font-size:11px;color:#aaa;margin-left:6px">{email_s}</span>
                                </div>
                                <div style="display:flex;gap:14px;align-items:center;font-size:12px">
                                    <span>{q_dot} <b>{sp}%</b></span>
                                    <span style="color:#bbb">🕐 {sub_time}</span>
                                </div>
                            </div>""", unsafe_allow_html=True)
                    else:
                        st.info("⏳ No submissions yet for this assignment.")


# ─────────────────────────────────────────────────────────────────
# STUDENT HOMEWORK VIEW
# ─────────────────────────────────────────────────────────────────
def page_student_homework():
    u = st.session_state.user
    st.markdown("<div class=\"section-header\">📋 My Homework</div>", unsafe_allow_html=True)

    homework = load_json(HOMEWORK_FILE)
    all_hw   = list(homework.values())
    grade    = u.get("grade","")

    # Filter: active assignments matching student's grade (or all if no grade set)
    active_hw = [
        h for h in all_hw
        if h.get("status","active") == "active"
        and (not grade or h.get("grade") == grade)
    ]

    submitted_ids = {h["id"] for h in all_hw if u["email"] in h.get("submissions",{})}
    pending  = [h for h in active_hw if h["id"] not in submitted_ids]
    done_hw  = [h for h in all_hw    if u["email"] in h.get("submissions",{})]

    # Summary bar
    total_a = len(active_hw)
    done_a  = len([h for h in active_hw if h["id"] in submitted_ids])
    pct_a   = int(done_a/max(total_a,1)*100)
    bar_col = "#059669" if pct_a>=70 else "#F59E0B" if pct_a>=40 else "#E8472A"

    st.markdown(f"""
    <div style="background:#fff;border-radius:14px;padding:14px 18px;
        margin-bottom:16px;box-shadow:0 2px 10px rgba(0,0,0,.06)">
        <div style="display:flex;justify-content:space-between;font-size:13px;
            font-weight:700;color:#666;margin-bottom:8px">
            <span>📊 Homework Progress</span>
            <span style="color:{bar_col}">{done_a}/{total_a} completed ({pct_a}%)</span>
        </div>
        <div style="background:#F0F0F8;border-radius:99px;height:10px;overflow:hidden">
            <div style="width:{pct_a}%;height:10px;border-radius:99px;
                background:linear-gradient(90deg,{bar_col},{bar_col}88)"></div>
        </div>
    </div>""", unsafe_allow_html=True)

    tab_pending, tab_done = st.tabs([
        f"📝  Pending ({len(pending)})",
        f"✅  Submitted ({len(done_hw)})"
    ])

    # ── PENDING TAB ─────────────────────────────────────────────
    with tab_pending:
        if not pending:
            st.success("🎉 All caught up! No pending homework.")
        for hw in sorted(pending, key=lambda x: x.get("due_date",""), reverse=False):
            data      = hw.get("data", {})
            info      = SUBJECTS.get(hw.get("subject","Maths"), {"emoji":"📚","color":"#2563EB"})
            col_c     = info["color"]
            due       = hw.get("due_date","")
            days_left = (datetime.date.fromisoformat(due) - datetime.date.today()).days if due else 0
            dl_color  = "#C0392B" if days_left<=0 else "#E8770A" if days_left<=2 else "#059669"
            dl_label  = ("Due Today!" if days_left==0
                         else f"⚠️ Overdue by {abs(days_left)}d" if days_left<0
                         else f"Due in {days_left}d")
            hw_title  = data.get("title", hw.get("topic","Homework"))
            questions = data.get("questions",[])
            show_h    = hw.get("show_hints", True)

            with st.expander(
                f"{info['emoji']} {hw_title} · {hw.get('grade','')} "
                f"· {hw.get('type','')} · {dl_label}"
            ):
                st.markdown(f"""
                <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px">
                    <span style="background:{col_c}18;color:{col_c};padding:3px 10px;
                        border-radius:99px;font-size:12px;font-weight:700">
                        {info['emoji']} {hw.get('subject','')}</span>
                    <span style="background:{col_c}18;color:{col_c};padding:3px 10px;
                        border-radius:99px;font-size:12px;font-weight:700">
                        📝 {hw.get('type','')}</span>
                    <span style="background:{col_c}18;color:{col_c};padding:3px 10px;
                        border-radius:99px;font-size:12px;font-weight:700">
                        🎯 {hw.get('difficulty','')}</span>
                    <span style="background:{dl_color}18;color:{dl_color};padding:3px 10px;
                        border-radius:99px;font-size:12px;font-weight:700">📅 {dl_label}</span>
                    <span style="background:#FFF8E7;color:#92400E;padding:3px 10px;
                        border-radius:99px;font-size:12px;font-weight:700">
                        ⏱️ {data.get('estimated_time','')}</span>
                </div>
                <div style="background:#F8FAFF;border-radius:10px;padding:10px 14px;
                    font-size:13px;color:#374151;margin-bottom:10px;border-left:3px solid {col_c}">
                    <b>📋 Instructions:</b> {data.get('instructions','')[:350]}
                </div>
                <div style="font-size:12px;color:#6B7280;margin-bottom:10px">
                    <b>🎯 Learning Objectives:</b> {data.get('learning_objectives','')}
                </div>""", unsafe_allow_html=True)

                if not questions:
                    st.warning("No questions found for this assignment.")
                    continue

                st.markdown(f"**📝 Answer all {len(questions)} questions "
                            f"({data.get('total_marks',0)} marks total)**")

                TYPE_ICONS = {
                    "MCQ":("🔵","#2563EB"),"short_answer":("📝","#059669"),
                    "long_answer":("📄","#7C3AED"),"problem":("🔢","#E8472A"),
                }
                answers = {}

                for qi, question in enumerate(questions):
                    q_type = question.get("type","MCQ")
                    t_icon, t_col = TYPE_ICONS.get(q_type, ("❓","#666"))
                    marks_lbl = f"{question.get('marks',1)} mark(s)"

                    st.markdown(f"""
                    <div style="background:#F8F9FA;border-radius:10px;
                        padding:12px 14px;margin-bottom:4px;
                        border-left:4px solid {t_col}">
                        <span style="background:{t_col}18;color:{t_col};padding:2px 8px;
                            border-radius:99px;font-size:11px;font-weight:700;
                            display:inline-block;margin-bottom:6px">
                            {t_icon} {q_type.replace('_',' ').title()} · {marks_lbl}
                        </span>
                        <div style="font-size:14px;font-weight:700;color:#1A1A2E;
                            margin-top:4px;line-height:1.5">
                            Q{qi+1}. {question['question']}
                        </div>
                    </div>""", unsafe_allow_html=True)

                    if show_h and question.get("hint"):
                        with st.expander(f"💡 Hint for Q{qi+1}"):
                            st.info(question["hint"])

                    if q_type == "MCQ" and question.get("options"):
                        answers[qi] = st.radio(
                            f"Answer Q{qi+1}",
                            question["options"],
                            key=f"hw_ans_{hw['id']}_{qi}",
                            label_visibility="collapsed"
                        )
                    elif q_type in ("short_answer",):
                        answers[qi] = st.text_input(
                            f"Answer Q{qi+1}",
                            placeholder="Write your answer here…",
                            key=f"hw_ans_{hw['id']}_{qi}",
                            label_visibility="collapsed"
                        )
                    else:
                        answers[qi] = st.text_area(
                            f"Answer Q{qi+1}",
                            placeholder="Write your detailed answer here…",
                            height=100,
                            key=f"hw_ans_{hw['id']}_{qi}",
                            label_visibility="collapsed"
                        )

                st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
                if st.button(f"📤 Submit Homework",
                             key=f"submit_hw_{hw['id']}",
                             use_container_width=True, type="primary"):
                    score = 0
                    total_marks = sum(q.get("marks",1) for q in questions)
                    for qi, question in enumerate(questions):
                        if question.get("type") == "MCQ":
                            if answers.get(qi,"").strip() == question.get("answer","").strip():
                                score += question.get("marks",1)

                    score_pct = int(score/max(total_marks,1)*100)

                    hw_fresh = load_json(HOMEWORK_FILE)
                    if hw["id"] in hw_fresh:
                        hw_fresh[hw["id"]].setdefault("submissions",{})
                        hw_fresh[hw["id"]]["submissions"][u["email"]] = {
                            "student_name": u["name"],
                            "answers":      {str(k):v for k,v in answers.items()},
                            "score":        score,
                            "total_marks":  total_marks,
                            "score_pct":    score_pct,
                            "submitted_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                        }
                        save_json(HOMEWORK_FILE, hw_fresh)
                        bump_stats(hw.get("subject","Maths"), hw.get("grade",""), score_pct>=60)
                        check_badges(u["email"])

                    grade_emoji = "🏆" if score_pct>=80 else "👍" if score_pct>=60 else "💪"
                    msg = (f"{grade_emoji} Submitted! MCQ score: **{score}/{total_marks}** ({score_pct}%)"
                           if any(q.get("type")=="MCQ" for q in questions)
                           else f"{grade_emoji} Homework submitted successfully!")
                    st.success(msg)
                    if hw.get("show_answers"):
                        st.info("💡 Check the Submitted tab to review model answers.")
                    st.balloons()
                    time.sleep(1.5); st.rerun()

    # ── SUBMITTED TAB ────────────────────────────────────────────
    with tab_done:
        if not done_hw:
            st.info("📭 No submitted homework yet.")
        for hw in sorted(done_hw, key=lambda x:x.get("due_date",""), reverse=True):
            data     = hw.get("data",{})
            sub      = hw["submissions"][u["email"]]
            info     = SUBJECTS.get(hw.get("subject","Maths"), {"emoji":"📚","color":"#2563EB"})
            sp       = sub.get("score_pct",0)
            dot      = "🟢" if sp>=80 else "🟡" if sp>=60 else "🔴"
            hw_title = data.get("title", hw.get("topic","Homework"))
            show_ans = hw.get("show_answers", True)

            with st.expander(
                f"{info['emoji']} {hw_title} · {dot} {sp}% "
                f"· Submitted {sub.get('submitted_at','')[:10]}"
            ):
                grade_lbl  = "🏆 Excellent" if sp>=80 else "👍 Good" if sp>=60 else "💪 Keep Practising"
                grade_col  = "#065F46"      if sp>=80 else "#92400E" if sp>=60 else "#991B1B"
                grade_bg   = "#D1FAE5"      if sp>=80 else "#FFF8E7" if sp>=60 else "#FEE2E2"

                st.markdown(f"""
                <div style="background:{grade_bg};border-radius:12px;
                    padding:14px 16px;margin-bottom:14px">
                    <div style="font-size:16px;font-weight:900;color:{grade_col};margin-bottom:4px">
                        {grade_lbl}
                    </div>
                    <div style="font-size:13px;color:{grade_col}">
                        Score: {sub.get('score',0)}/{sub.get('total_marks',0)} ({sp}%)
                        · Submitted: {sub.get('submitted_at','')}
                    </div>
                </div>""", unsafe_allow_html=True)

                if show_ans:
                    questions       = data.get("questions",[])
                    student_answers = sub.get("answers",{})
                    st.markdown("#### 📋 Question Review")

                    for qi, question in enumerate(questions):
                        student_ans = student_answers.get(str(qi),"—")
                        correct_ans = question.get("answer","")
                        is_mcq      = question.get("type") == "MCQ"
                        is_correct  = (student_ans.strip()==correct_ans.strip()) if is_mcq else None
                        bg     = "#F0FDF4" if is_correct else "#FFF1EE" if is_correct is False else "#F8F9FA"
                        b_col  = "#059669" if is_correct else "#E8472A" if is_correct is False else "#ccc"
                        wrong  = (f"<div style='font-size:12px;color:#059669;margin-top:2px'>"
                                  f"✅ Correct: <b>{correct_ans}</b></div>"
                                  if is_mcq and not is_correct else "")
                        expl   = question.get("explanation","")
                        expl_html = (f"<div style='font-size:11px;color:#3730A3;margin-top:4px;"
                                     f"padding:5px 8px;background:rgba(99,102,241,0.08);"
                                     f"border-radius:6px'>📖 {expl}</div>" if expl else "")

                        st.markdown(f"""
                        <div style="background:{bg};border-radius:10px;padding:10px 14px;
                            margin-bottom:6px;border-left:3px solid {b_col}">
                            <div style="font-size:13px;font-weight:700;color:#1A1A2E">
                                Q{qi+1}. {question['question'][:110]}</div>
                            <div style="font-size:12px;color:#555;margin-top:4px">
                                Your answer: <b>{student_ans}</b>
                                {"✅" if is_correct else "❌" if is_correct is False else ""}
                            </div>
                            {wrong}{expl_html}
                        </div>""", unsafe_allow_html=True)
                else:
                    st.info("Answers will be shown after the due date.")



# ─────────────────────────────────────────────────────────────────
# ROUTER
# ─────────────────────────────────────────────────────────────────
# ── LOGIN BYPASS (demo mode — re-enable page_auth() when ready) ──
if not st.session_state.logged_in:
    st.session_state.logged_in = True
    st.session_state.user = {
        "email":   "demo@zmacademy.pk",
        "name":    "Demo Student",
        "grade":   "Grade 9",
        "role":    "student",
        "avatar":  "👨‍🎓",
        "plan":    "free",
        "badges":  [],
        "stats":   init_stats(),
        "is_new":  False,
    }
    st.rerun()

render_sidebar()
p = st.session_state.page
if   p == "home":        page_home()
elif p == "chat":        page_chat()
elif p == "syllabus":    page_syllabus()
elif p == "quiz":        page_quiz()
elif p == "friends":     page_friends()
elif p == "image":       page_image()
elif p == "homework":    page_homework()
elif p == "my_homework": page_student_homework()
elif p == "admin":       page_admin()
elif p == "progress":    page_progress()
elif p == "history":     page_history()
elif p == "badges":      page_badges()
elif p == "profile":     page_profile()
