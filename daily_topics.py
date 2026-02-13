# daily_topics.py
from datetime import datetime
import random
import time
import logging
from utils.topic_provider import TopicProvider


class DailyTopics(TopicProvider):
    def __init__(self):
        self.topics_by_day = {
            'Monday': [
                'Behavioral Patterns of Primates', 'Migration Routes of Monarch Butterflies', 'Predatory Strategies in Big Cats', 'Social Structures in Elephant Herds', 'Nocturnal Adaptations in Animals', 'Reproductive Behavior in Amphibians', 'Role of Zoology in Species Conservation', 'Courtship Rituals in Birds', 'Communication in Dolphin Pods', 'Camouflage and Mimicry in Insects', 'Echolocation in Bats and Whales', 'Parental Care in Marsupials', 'Interspecies Symbiotic Relationships', 'Role of Genetics in Animal Behavior', 'Animal Intelligence and Problem-Solving', 'Seasonal Breeding in Arctic Species', 'Ethology and Its Applications', 'Mating Systems in Mammals', 'Territorial Behavior in Reptiles', 'Warning Coloration in Poisonous Animals', 'Animal Social Hierarchies', 'Zoology in Studying Extinct Fauna', 'Hibernation Mechanisms in Mammals', 'Role of Pheromones in Animal Interaction', 'Pack Hunting in Wolves', 'Tool Use in Crows and Apes', 'Animal Navigation Without GPS', 'Bird Migration and Magnetic Fields', 'Mimicry vs. Camouflage in Defense', 'Sexual Dimorphism in Animal Species', 'Bioluminescence in Deep Sea Creatures', 'Keystone Species and Ecosystem Balance', 'Domestication of Animals', 'Animal Communication Systems', 'Maternal Instincts in Birds', 'Courtship Displays in Peacocks', 'Sensory Adaptations in Predators', 'Social Grooming in Primates', 'Ant Colony Hierarchies', 'Roles of Zoologists in Zoos', 'Endangered Species Recovery Programs', 'Ethical Considerations in Animal Research', 'Animal Migration Due to Climate Change', 'Territory Marking in Mammals', 'Animal Emotions and Sentience', 'Zoology and Marine Mammal Studies', 'Intelligence Testing in Octopuses', 'Seasonal Fur Changes in Arctic Foxes', 'Comparative Anatomy in Vertebrates', 'Role of Enzymes in Animal Digestion'
            ],
            'Tuesday': [
                'Newtons Laws of Motion', 'Quantum Tunneling', 'Electromagnetic Induction', 'Thermodynamic Equilibrium', 'Superconductivity Phenomena', 'Gravitational Waves', 'Photoelectric Effect', 'Centripetal Force Applications', 'Relativity of Simultaneity', 'Wave-Particle Duality', 'Blackbody Radiation', 'Resonance in Oscillating Systems', 'Rotational Dynamics', 'Lorentz Transformation', 'Kinetic Theory of Gases', 'Nuclear Fusion Mechanisms', 'Coulomb\'s Law in Practice', 'Electromagnetic Spectrum', 'Gravitational Potential Energy', 'Interference of Light Waves', 'Semiconductor Physics', 'Capacitor Charging Curves', 'Electric Field Lines', 'Hooke\'s Law in Elasticity', 'Conservation of Angular Momentum', 'Photon Behavior in Optics', 'Time Dilation Effects', 'Fluid Statics Principles', 'Magnetic Flux in Circuits', 'Heisenberg\'s Uncertainty Principle', 'Energy Quantization in Atoms', 'Thermal Expansion of Solids', 'Projectile Motion Analysis', 'Bernoulli\'s Equation in Fluids', 'Tension in Cables and Strings', 'String Theory Concepts', 'Solar Radiation Pressure', 'Friction and Surface Interactions', 'Elastic and Inelastic Collisions', 'Standing Waves in Pipes', 'Polarization of Light', 'Radioactive Decay Law', 'Viscosity and Laminar Flow', 'Magnetic Field of a Solenoid', 'Diffraction of Sound Waves', 'Electric Potential Difference', 'Doppler Effect Applications', 'Work-Energy Theorem', 'Harmonic Motion in Springs'
            ],
            'Wednesday': [
                'Periodic Table Trends', 'Electronegativity Differences', 'Molecular Orbital Theory', 'Acid-Base Titrations', 'Electrochemical Cells', 'Redox Reactions', 'Chemical Bonding Models', 'Le Chatelier\'s Principle', 'Atomic Structure Theories', 'Covalent Bond Characteristics', 'Transition Metal Complexes', 'Hybridization in Molecules', 'Ionic Compounds Formation', 'Aromaticity in Benzene', 'Gibbs Free Energy', 'Thermochemistry and Heat Flow', 'Intermolecular Forces', 'Organic Reaction Mechanisms', 'Rate Laws in Kinetics', 'Reaction Coordinate Diagrams', 'Hess\'s Law Calculations', 'Stoichiometry Applications', 'Molecular Polarity and Dipoles', 'Collision Theory', 'Activation Energy Concept', 'Nucleophilic Substitution Reactions', 'Elimination Reaction Mechanisms', 'Enthalpy vs Entropy', 'Phase Equilibrium Diagrams', 'Lewis Acid and Base Theory', 'Haber Process for Ammonia', 'Molecular Geometry via VSEPR', 'Hydrocarbon Structures', 'Crude Oil Fractional Distillation', 'Polarity in Organic Compounds', 'Hydrogen Bonding in Water', 'Saponification Process', 'Buffer Systems in Blood', 'Complex Ion Formation', 'Chromatography Techniques'
            ],
            'Thursday': [
                'Budgeting for Beginners', 'Emergency Fund Planning', 'High-Yield Savings Accounts', 'Compound Interest Explained', 'Debt Snowball Method', 'Debt Avalanche Strategy', 'Paying Off Student Loans', 'Understanding Credit Scores', 'Credit Report Monitoring', 'Secured vs. Unsecured Loans', 'Building Credit from Scratch', 'Best Budgeting Apps', 'Sinking Funds Strategy', 'Creating a Monthly Budget', 'Managing Irregular Income', 'How to Avoid Lifestyle Inflation', '50/30/20 Rule Explained', 'Zero-Based Budgeting', 'Financial Goal Setting', 'Cash Envelope System', 'Retirement Planning 101', 'Roth IRA vs. Traditional IRA', '401(k) Contribution Strategies', 'Early Retirement Planning', 'How to Avoid Bank Fees', 'Checking vs. Savings Accounts', 'Intro to Index Funds', 'Dollar-Cost Averaging', 'Tax-Efficient Investing', 'Choosing a Financial Advisor', 'Understanding Mutual Funds', 'ETFs for Beginners', 'Asset Allocation Basics', 'Emergency Fund vs. Investment', 'CDs vs. Bonds', 'Target-Date Retirement Funds', 'Passive Income Streams', 'Side Hustle Ideas', 'Digital Banks vs. Traditional Banks', 'Setting Up Direct Deposits'
            ],
            'Friday': [
                'The Rise of Digital Journalism', 'Media Bias in News Coverage', 'Evolution of Print Media', 'Impact of Social Media on News', 'Citizen Journalism Trends', 'Challenges Facing Traditional Newspapers', 'Fake News Detection Techniques', 'Freedom of Press Worldwide', 'Media Literacy Education', 'Photojournalism Ethics', 'Clickbait and Its Consequences', 'The Role of Media in Elections', 'Media Consolidation and Monopoly', 'Streaming Wars: Netflix vs. Competitors', 'Censorship in Modern Media', 'Globalization of News Content', '24-Hour News Cycle Impact', 'Rise of Podcasting', 'Viral Media Phenomena', 'Deepfakes in News Media', 'Role of AI in Content Creation', 'Ethics of Investigative Journalism', 'Influencer Marketing in Media', 'Branded Content Strategies', 'Data Journalism Techniques', 'Visual Storytelling in News', 'Documentary Filmmaking Trends', 'Subscription-Based News Models', 'Paywalls and Free Access Debate', 'YouTube as a News Platform', 'The Evolution of TV Journalism', 'Public vs. Private Broadcasting', 'Media and Public Opinion', 'Fact-Checking Organizations', 'Disinformation Campaigns', 'Role of Media in Social Movements'
            ],
            'Saturday': [
                'Federalism vs. Unitarism', 'Constitutional Amendments', 'Role of the Judiciary in Democracy', 'Electoral College Explained', 'Parliamentary vs. Presidential Systems', 'Left-Wing vs. Right-Wing Ideologies', 'Progressive vs. Conservative Views', 'Checks and Balances in Government', 'Gerrymandering and Redistricting', 'Role of Lobbyists in Legislation', 'Voting Rights and Suppression', 'Campaign Finance Reform', 'Political Polarization Trends', 'Global Populist Movements', 'Rise of Authoritarian Regimes', 'Freedom of Speech in Politics', 'Political Campaign Strategy', 'Role of Political Parties', 'Coalition Governments Explained', 'Constituency Representation', 'Direct vs. Representative Democracy', 'Bicameral vs. Unicameral Legislatures', 'Voter Turnout Trends', 'Identity Politics and Governance', 'Foreign Policy Decision-Making', 'Role of the Military in Politics', 'Public Opinion and Policy Making', 'Role of the Media in Elections', 'Political Debate Ethics', 'Political Advertising Techniques', 'E-voting Security Challenges', 'Civic Nationalism vs. Ethnic Nationalism', 'Globalism vs. Isolationism', 'Separatist Movements Worldwide', 'International Sanctions Policy', 'Trade Agreements and Politics'
            ],
            'Sunday': [
                'Phishing Attack Prevention', 'Ransomware Attack Response', 'Malware Types and Detection', 'Firewall Configuration Basics', 'Antivirus vs. Anti-Malware', 'Zero-Day Exploit Awareness', 'DDoS Attack Mitigation', 'Password Management Best Practices', 'Multi-Factor Authentication (MFA)', 'Biometric Security Systems', 'Understanding Social Engineering', 'Cybersecurity Risk Assessment', 'Vulnerability Scanning Tools', 'Penetration Testing Techniques', 'Intrusion Detection Systems (IDS)', 'Intrusion Prevention Systems (IPS)', 'Email Spoofing Detection', 'Man-in-the-Middle Attack Defense', 'SQL Injection Explained', 'Cross-Site Scripting (XSS)', 'Broken Access Control', 'Cybersecurity Frameworks (NIST)', 'Cyber Hygiene Practices', 'Security Patches and Updates', 'Cloud Security Best Practices', 'Mobile Device Security', 'Secure File Transfer Protocols', 'Encryption Algorithms Overview', 'Public Key Infrastructure (PKI)', 'SSL/TLS Protocols', 'Network Segmentation Strategy', 'Zero Trust Architecture', 'Cybersecurity Policy Writing', 'Security Awareness Training', 'Insider Threat Mitigation', 'SIEM Systems Explained'
            ]
        }

        self._current_day_key = None
        self._shuffled_today_topics = []
        self._shuffled_index = 0

    def get_topics_for_today(self):
        """Returns today's topics based on current day of week"""
        day_name = datetime.now().strftime('%A')
        return self.topics_by_day.get(day_name, self._get_default_topics())

    def next_topic_for_today(self):
        """Return the next topic for today, randomly selected without repetition."""
        day_name = datetime.now().strftime('%A')
        if self._current_day_key != day_name or not self._shuffled_today_topics:
            topics = list(self.topics_by_day.get(day_name, self._get_default_topics()))
            random_seed = int(datetime.now().timestamp())
            random.Random(random_seed).shuffle(topics)
            self._shuffled_today_topics = topics
            self._shuffled_index = 0
            self._current_day_key = day_name

        if self._shuffled_index >= len(self._shuffled_today_topics):
            topics = list(self._shuffled_today_topics)
            random.Random(int(time.time())).shuffle(topics)
            self._shuffled_today_topics = topics
            self._shuffled_index = 0

        topic = self._shuffled_today_topics[self._shuffled_index]
        self._shuffled_index += 1
        return topic

    def _get_default_topics(self):
        """Fallback topics if day not found"""
        return ['Current world news', 'Scientific discoveries', 'Technology trends', 'Educational resources']

    def get_all_topics(self):
        """Returns all topics organized by day (for debugging/display)"""
        return self.topics_by_day

    def reset(self):
        """Reset provider state (TopicProvider interface implementation)"""
        self._current_day_key = None
        self._shuffled_today_topics = []
        self._shuffled_index = 0
        logging.getLogger(__name__).info("DailyTopics reset")

    def get_statistics(self):
        """Get provider statistics (TopicProvider interface implementation)"""
        return {
            'total_days': len(self.topics_by_day),
            'topics_per_day': {day: len(topics) for day, topics in self.topics_by_day.items()},
            'generator_type': 'DailyTopics',
            'current_day': self._current_day_key
        }
