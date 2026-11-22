-- =======================================================
-- AyuCare Seed Data Script
-- Project: आयुCare (AyuCare) - Initial Dataset
-- Contains: 11 Specialists, Sample Doctors, 50 Symptoms & Guidance, Chatbot FAQs
-- =======================================================

USE `ayucare_db`;

-- 1. Insert Specialists
INSERT INTO `specialists` (`id`, `name`, `description`, `common_conditions`, `icon`) VALUES
(1, 'General Physician', 'Primary care medical doctors providing non-surgical comprehensive healthcare for common, acute, and routine conditions.', 'Fever, flu, fatigue, infections, general malaise, dehydration', 'fa-user-doctor'),
(2, 'Cardiologist', 'Specialist dealing with disorders of the heart and blood vessels.', 'Chest pain, palpitations, hypertension, cold extremities, shortness of breath', 'fa-heart-pulse'),
(3, 'Dermatologist', 'Medical practitioner qualified to diagnose and treat skin, hair, and nail disorders.', 'Rashes, acne, dry skin, severe itching, eczema, hives, skin infections', 'fa-hand-dots'),
(4, 'Neurologist', 'Specialist in the anatomy, functions, and organic disorders of nerves and the nervous system.', 'Migraines, persistent dizziness, chronic headaches, numbness, seizures', 'fa-brain'),
(5, 'Orthopedic Specialist', 'Surgeon and specialist focused on the musculoskeletal system (bones, joints, ligaments, tendons).', 'Joint pain, back pain, knee pain, shoulder stiffness, neck pain, muscle cramps', 'fa-bone'),
(6, 'ENT Specialist', 'Otolaryngologist managing conditions related to the ear, nose, throat, and vocal cords.', 'Ear pain, sore throat, nasal congestion, runny nose, hoarseness, sinusitis', 'fa-head-side-cough'),
(7, 'Ophthalmologist', 'Medical doctor specializing in the diagnosis and treatment of eye disorders and vision care.', 'Eye redness, dry eyes, watery eyes, vision blurriness, eye strain', 'fa-eye'),
(8, 'Gastroenterologist', 'Specialist focused on diseases of the digestive system and liver.', 'Stomach pain, persistent vomiting, diarrhea, constipation, bloating, indigestion', 'fa-stethoscope'),
(9, 'Dentist', 'Healthcare provider specializing in oral health, teeth, gums, and oral cavity.', 'Tooth sensitivity, bleeding gums, mouth ulcers, toothache, bad breath', 'fa-tooth'),
(10, 'Gynecologist', 'Physician specializing in female reproductive health and wellness.', 'Menstrual cramps, pelvic pain, hormonal imbalances, irregular cycles', 'fa-person-dress'),
(11, 'Psychiatrist', 'Medical physician specializing in mental health, emotional wellness, and sleep health.', 'Mild anxiety, insomnia, sleep difficulty, persistent stress, mood changes', 'fa-couch')
ON DUPLICATE KEY UPDATE `name`=VALUES(`name`);

-- 2. Insert Sample Doctors
-- Passwords below are hashed for 'Doctor@123' (PBKDF2 SHA256)
INSERT INTO `doctors` (`id`, `full_name`, `email`, `mobile`, `specialization`, `registration_number`, `password_hash`, `verification_status`, `bio`, `experience_years`, `hospital_clinic`) VALUES
(1, 'Dr. Rajesh Sharma', 'dr.rajesh@ayucare.in', '+919876543210', 'General Physician', 'MCI-34821', 'pbkdf2:sha256:600000$ayucare_salt$5ce25422f7a899cf4ed7c6d8018cff66d221cfb02ea63713557026ae3b7c16cf', 'verified', 'Senior Physician with over 15 years of clinical practice in preventive medicine and family healthcare.', 15, 'Apollo Health Clinic, Mumbai'),
(2, 'Dr. Sunita Patel', 'dr.sunita@ayucare.in', '+919876543211', 'Dermatologist', 'MCI-89211', 'pbkdf2:sha256:600000$ayucare_salt$5ce25422f7a899cf4ed7c6d8018cff66d221cfb02ea63713557026ae3b7c16cf', 'verified', 'Consultant Dermatologist specializing in clinical dermatology, skin allergies, and acne management.', 10, 'Skin & Wellness Care, Delhi'),
(3, 'Dr. Amitav Sen', 'dr.amitav@ayucare.in', '+919876543212', 'Orthopedic Specialist', 'MCI-45192', 'pbkdf2:sha256:600000$ayucare_salt$5ce25422f7a899cf4ed7c6d8018cff66d221cfb02ea63713557026ae3b7c16cf', 'verified', 'Orthopedic consultant with expertise in joint preservation, sports injuries, and posture correction.', 12, 'Orthocare Super Specialty, Bengaluru'),
(4, 'Dr. Priya Nambiar', 'dr.priya@ayucare.in', '+919876543213', 'ENT Specialist', 'MCI-77341', 'pbkdf2:sha256:600000$ayucare_salt$5ce25422f7a899cf4ed7c6d8018cff66d221cfb02ea63713557026ae3b7c16cf', 'verified', 'Otolaryngologist focused on sinusitis, pediatric ENT, and vocal health.', 9, 'Sunrise Care Hospital, Kochi'),
(5, 'Dr. Vikramaditya Rao', 'dr.vikram@ayucare.in', '+919876543214', 'Gastroenterologist', 'MCI-66299', 'pbkdf2:sha256:600000$ayucare_salt$5ce25422f7a899cf4ed7c6d8018cff66d221cfb02ea63713557026ae3b7c16cf', 'verified', 'Digestive health specialist experienced in irritable bowel disorders, acid reflux, and liver care.', 14, 'Max Health Institute, Pune'),
(6, 'Dr. Ananya Roy', 'dr.ananya@ayucare.in', '+919876543215', 'Cardiologist', 'MCI-19482', 'pbkdf2:sha256:600000$ayucare_salt$5ce25422f7a899cf4ed7c6d8018cff66d221cfb02ea63713557026ae3b7c16cf', 'verified', 'Preventive cardiologist focused on heart health, lifestyle modification, and vascular care.', 11, 'Heart Care Centre, Hyderabad'),
(7, 'Dr. Rohan Verma', 'dr.rohan@ayucare.in', '+919876543216', 'Neurologist', 'MCI-90412', 'pbkdf2:sha256:600000$ayucare_salt$5ce25422f7a899cf4ed7c6d8018cff66d221cfb02ea63713557026ae3b7c16cf', 'pending', 'Neurology registrar passionate about headache management and neurological wellness.', 4, 'City Neuro Clinic, Ahmedabad')
ON DUPLICATE KEY UPDATE `full_name`=VALUES(`full_name`);

-- 3. Insert 50 Symptoms
INSERT INTO `symptoms` (`id`, `name`, `category`, `description`, `urgency_level`, `warning_signs`, `specialist_id`) VALUES
(1, 'Fever', 'General', 'Elevation in internal body temperature above normal range (typically > 37.5°C or 99.5°F).', 'Moderate', 'Temperature > 103°F (39.4°C), stiff neck, severe headache, confusion, difficulty breathing, rash.', 1),
(2, 'Headache', 'Neurological', 'Pain or discomfort in the head, scalp, or upper neck area.', 'Mild', 'Sudden severe "thunderclap" onset, visual changes, stiff neck, slurred speech, confusion.', 4),
(3, 'Migraine', 'Neurological', 'Recurrent throbbing headache typically affecting one side, often with sensitivity to light and sound.', 'Moderate', 'Sudden severe attack unlike previous ones, loss of vision, weakness in arms or legs.', 4),
(4, 'Cough', 'Respiratory', 'Reflex action to clear airway of irritants, mucus, or foreign particles.', 'Mild', 'Coughing up blood, high fever, chest pain, wheezing, shortness of breath, lasting > 3 weeks.', 1),
(5, 'Sore throat', 'ENT & Eyes', 'Pain, scratchiness, or irritation of the throat that often worsens when swallowing.', 'Mild', 'Inability to swallow fluids, drooling, difficulty breathing, neck stiffness, high fever.', 6),
(6, 'Runny nose', 'ENT & Eyes', 'Excess drainage produced by nasal tissues, ranging from clear fluid to thick mucus.', 'Mild', 'Clear fluid draining after head injury, high fever, facial tenderness, symptoms lasting > 10 days.', 6),
(7, 'Sneezing', 'ENT & Eyes', 'Sudden, involuntary expulsion of air from nose and mouth due to mucosal irritation.', 'Mild', 'Accompanied by high fever, wheezing, difficulty breathing, or severe facial swelling.', 6),
(8, 'Nasal congestion', 'ENT & Eyes', 'Blockage in nasal passages due to swollen nasal cavity membranes from inflamed blood vessels.', 'Mild', 'High fever, swelling around eyes or forehead, vision changes, stiff neck.', 6),
(9, 'Skin rash', 'Skin', 'Noticeable change in texture or color of the skin, may be itchy, red, bumpy, or irritated.', 'Moderate', 'Rapidly spreading purple spots, breathing difficulty, swelling of lips/tongue, blistered skin.', 3),
(10, 'Itching', 'Skin', 'Irritating sensation creating an urge to scratch, also known as pruritus.', 'Mild', 'Associated with yellowing of eyes/skin (jaundice), severe unexplained weight loss, night sweats.', 3),
(11, 'Acne', 'Skin', 'Skin condition that occurs when hair follicles become plugged with oil and dead skin cells.', 'Mild', 'Severe cystic nodules causing painful swelling, severe scarring, signs of bacterial infection.', 3),
(12, 'Dry skin', 'Skin', 'Common condition with lack of appropriate moisture in the epidermis leading to scaling or peeling.', 'Mild', 'Cracking that bleeds or oozes, signs of infection like redness, warmth, or pus.', 3),
(13, 'Ear pain', 'ENT & Eyes', 'Discomfort, sharp pain, or pressure sensation localized in the ear canal or surrounding area.', 'Moderate', 'Fluid or blood draining from ear, sudden hearing loss, severe dizziness, swelling behind ear.', 6),
(14, 'Eye redness', 'ENT & Eyes', 'Red or bloodshot appearance of the white portion of the eye (sclera).', 'Mild', 'Severe eye pain, sensitivity to light, blurred vision, discharge with crusting, recent eye trauma.', 7),
(15, 'Watery eyes', 'ENT & Eyes', 'Excessive tear production or inadequate tear drainage leading to overflowing tears.', 'Mild', 'Severe eye pain, sudden vision changes, thick yellowish pus, foreign object sensation.', 7),
(16, 'Stomach pain', 'Digestive', 'Discomfort, cramping, or aching felt anywhere in the abdominal region.', 'Moderate', 'Severe acute pain, rigid or tender abdomen, vomiting blood, black tarry stools, high fever.', 8),
(17, 'Nausea', 'Digestive', 'Uneasiness or discomfort in upper stomach accompanied by involuntary urge to vomit.', 'Mild', 'Accompanied by chest pain, confusion, severe abdominal pain, high fever, or head trauma.', 8),
(18, 'Vomiting', 'Digestive', 'Forceful voluntary or involuntary expulsion of stomach contents through the mouth.', 'Moderate', 'Inability to keep liquids down for 24 hours, blood in vomit, signs of severe dehydration, stiff neck.', 8),
(19, 'Diarrhea', 'Digestive', 'Frequent passage of loose, watery stools occurring more than three times in a day.', 'Moderate', 'Bloody stools, high fever (> 102°F), signs of severe dehydration (sunken eyes, dizziness), lasting > 48h.', 8),
(20, 'Constipation', 'Digestive', 'Infrequent bowel movements or difficult passage of stools that persists for several days.', 'Mild', 'Severe abdominal pain, vomiting, inability to pass gas, blood in stool, unexplained weight loss.', 8),
(21, 'Indigestion', 'Digestive', 'Discomfort or burning sensation in upper abdomen, often associated with fullness or nausea.', 'Mild', 'Chest pain radiating to arm, jaw or back, shortness of breath, unexplained weight loss, vomiting blood.', 8),
(22, 'Bloating', 'Digestive', 'Feeling of fullness, tightness, or swollen appearance in the abdominal region.', 'Mild', 'Severe persistent pain, unexplained weight loss, blood in stool, ascites (fluid accumulation).', 8),
(23, 'Joint pain', 'Musculoskeletal', 'Discomfort, aches, or soreness arising from any joint in the body.', 'Moderate', 'Joint red, hot to touch, swollen, accompanied by fever, or inability to bear weight.', 5),
(24, 'Back pain', 'Musculoskeletal', 'Ache, stiffness, or sharp pain felt along the spine, upper back, or lumbar area.', 'Mild', 'Loss of bowel or bladder control, numbness in groin or legs, pain following high-impact trauma.', 5),
(25, 'Neck pain', 'Musculoskeletal', 'Soreness, stiffness, or spasms in neck muscles or cervical spine vertebrae.', 'Mild', 'Accompanied by fever and stiff neck (inability to touch chin to chest), numbness radiating to arm.', 5),
(26, 'Shoulder pain', 'Musculoskeletal', 'Aching or restricted mobility around the shoulder joint, rotator cuff, or upper arm.', 'Mild', 'Sudden pain accompanied by chest tightness, shortness of breath, dizziness (call emergency).', 5),
(27, 'Knee pain', 'Musculoskeletal', 'Pain in or around the knee joint caused by strain, overuse, or mechanical stress.', 'Mild', 'Inability to bear weight, visible deformity, loud popping sound followed by immediate swelling.', 5),
(28, 'Muscle cramps', 'Musculoskeletal', 'Sudden, involuntary, and painful contractions of one or more muscles, often in calves.', 'Mild', 'Severe swelling, redness or warmth in the calf (sign of deep vein thrombosis), severe weakness.', 5),
(29, 'Fatigue', 'General', 'Persistent feeling of tiredness, lack of energy, or mental/physical exhaustion.', 'Mild', 'Chest pain, shortness of breath, irregular heartbeat, sudden severe muscle weakness.', 1),
(30, 'Dizziness', 'Neurological', 'Sensation of lightheadedness, unsteadiness, or feeling faint.', 'Moderate', 'Sudden weakness, facial droop, slurred speech, chest pain, fainting (syncope), severe headache.', 4),
(31, 'Loss of appetite', 'Digestive', 'Reduced desire to eat or premature feeling of fullness after eating small quantities.', 'Mild', 'Rapid unintentional weight loss, severe stomach pain, jaundice, persistent vomiting.', 1),
(32, 'Mild dehydration', 'General', 'State where body fluid loss slightly exceeds intake, causing thirst and dry mouth.', 'Mild', 'Extreme thirst, confusion, no urination for > 8 hours, sunken eyes, rapid pulse (emergency).', 1),
(33, 'Allergy symptoms', 'ENT & Eyes', 'Hypersensitive immune response manifesting as sneezing, itchy eyes, or mild nasal drip.', 'Mild', 'Swelling of throat, lips, tongue, wheezing, hives, dizziness (anaphylaxis - emergency).', 1),
(34, 'Sunburn', 'Skin', 'Red, painful, warm skin resulting from excessive exposure to ultraviolet (UV) radiation.', 'Mild', 'Large blisters covering substantial body area, high fever, chills, dizziness, confusion.', 3),
(35, 'Minor burn', 'Skin', 'Superficial first-degree thermal burn causing redness, mild swelling, and localized pain.', 'Mild', 'Blistering larger than 2 inches, burn on face/hands/genitals, charred or white skin (emergency).', 3),
(36, 'Insect bite', 'Skin', 'Localized puncture wound from insect causing redness, slight swelling, and itching.', 'Mild', 'Difficulty breathing, swelling of face or throat, hives across body, feeling dizzy (emergency).', 3),
(37, 'Motion sickness', 'General', 'Disagreement between visual perception and vestibular inner ear balance system while traveling.', 'Mild', 'Severe chest pain, persistent vomiting preventing hydration, loss of consciousness.', 1),
(38, 'Hiccups', 'Digestive', 'Involuntary repetitive spasms of diaphragm accompanied by quick closure of vocal cords.', 'Mild', 'Hiccups persisting for more than 48 hours, difficulty breathing, chest pain, trouble swallowing.', 1),
(39, 'Bad breath', 'Dentistry', 'Unpleasant odor exhaled from the mouth, clinically termed halitosis.', 'Mild', 'Persistent bleeding gums, loose teeth, mouth sores that do not heal within 2 weeks.', 9),
(40, 'Tooth sensitivity', 'Dentistry', 'Brief sharp discomfort or twinge triggered by hot, cold, sweet, or acidic foods and drinks.', 'Mild', 'Severe spontaneous throbbing pain, facial swelling, fever, foul taste in mouth.', 9),
(41, 'Bleeding gums', 'Dentistry', 'Bleeding along the gumline while brushing, flossing, or eating firm foods.', 'Moderate', 'Spontaneous heavy bleeding, loose permanent teeth, receding gum line with severe pain.', 9),
(42, 'Mouth ulcer', 'Dentistry', 'Painful small shallow lesion or sore developing on gums, inner cheeks, or tongue (aphthous ulcer).', 'Mild', 'Ulcer persisting beyond 2 weeks, unusually large sore, difficulty swallowing or fever.', 9),
(43, 'Chapped lips', 'Skin', 'Dry, cracked, peeling, or irritated lips due to dry air, dehydration, or lip licking.', 'Mild', 'Cracking that bleeds continuously, persistent crusting, lack of improvement after 10 days.', 3),
(44, 'Dry eyes', 'ENT & Eyes', 'Stinging, gritty, or burning sensation when eyes do not produce sufficient lubricating tears.', 'Mild', 'Severe pain, marked decrease in vision, sensitivity to light, redness that spreads.', 7),
(45, 'Hoarseness', 'ENT & Eyes', 'Abnormal change in pitch or quality of voice, sounding raspy, strained, or breathy.', 'Mild', 'Hoarseness lasting > 2 weeks, difficulty swallowing or breathing, coughing up blood, neck lump.', 6),
(46, 'Mild anxiety', 'Mental Health', 'Feelings of mild tension, nervous worry, or stress about everyday challenges.', 'Mild', 'Panic attacks, thoughts of self-harm, chest pain, inability to function in daily life.', 11),
(47, 'Sleep difficulty', 'Mental Health', 'Occasional trouble falling asleep or waking up repeatedly during nighttime.', 'Mild', 'Severe daytime drowsiness causing safety risks, severe mood disturbance, loud gasping/apnea.', 11),
(48, 'Mild leg swelling', 'General', 'Slight puffiness or fluid retention in ankles or feet after prolonged standing or sitting.', 'Moderate', 'Sudden swelling in one leg only with warmth/pain (DVT risk), chest pain, shortness of breath.', 1),
(49, 'Menstrual cramps', 'Women Health', 'Throbbing or cramping pains in lower abdomen before and during menstrual periods (dysmenorrhea).', 'Mild', 'Severe debilitating pain, fever, foul-smelling vaginal discharge, sudden pelvic tenderness.', 10),
(50, 'Cold hands', 'General', 'Hands feeling unusually chilly or sensitive to cool ambient temperatures.', 'Mild', 'Fingers turning white, blue then red with numbness (Raynaud phenomenon), skin sores, chest pain.', 1)
ON DUPLICATE KEY UPDATE `name`=VALUES(`name`);

-- 4. Insert Symptom Guidance & Mild Home-Care Information
-- Note: Home care is populated ONLY when clinically safe and appropriate for mild conditions.
-- For higher urgency or where home treatment is clinically inappropriate, mild_home_care is set to NULL or safe supportive comfort measures only.
INSERT INTO `symptom_guidance` (`id`, `symptom_id`, `preliminary_guidance`, `mild_home_care`, `warning_signs_details`, `reference_source`) VALUES
(1, 1, 'Rest adequately and keep hydration high. Monitor body temperature with a clean digital thermometer every 4-6 hours.', 
 'Drink plenty of water, tender coconut water, and clear broths. Rest in a well-ventilated room wearing light clothing. Use a lukewarm damp cloth for forehead sponging if comfortable. Avoid cold water baths.', 
 'Seek emergency care if fever exceeds 103°F (39.4°C), or is accompanied by stiff neck, shortness of breath, confusion, or convulsions.', 'WHO Family Health Guidelines'),

(2, 2, 'Most mild headaches are tension-type or stress-induced. Note frequency, timing, and any possible triggers like screen fatigue or dehydration.', 
 'Rest in a quiet, dimly lit room. Drink a glass of water. Practice gentle neck and shoulder stretching. Apply a cool or warm compress to forehead or back of neck.', 
 'Seek immediate medical attention for sudden "thunderclap" headache, neurological deficits, slurred speech, or headache following head injury.', 'Mayo Clinic Neurology'),

(3, 3, 'Migraines are complex neurovascular events. Keep a headache diary tracking potential triggers such as sleep disruption, bright lights, or specific foods.', 
 'Rest in a dark, quiet environment. Apply an ice pack wrapped in a cloth to the temples or forehead. Stay hydrated and avoid known dietary triggers.', 
 'Consult a neurologist if migraine attacks become more frequent, or if visual aura persists beyond 60 minutes.', 'American Migraine Foundation'),

(4, 4, 'Cough is a natural protective reflex. Determine whether cough is dry or producing phlegm. Avoid exposure to smoke, dust, and cold dry air.', 
 'Sip warm water, herbal teas, or warm water with honey (for adults and children over 1 year). Inhale warm steam to loosen chest mucus. Use a room humidifier.', 
 'Consult a physician if coughing up rust-colored phlegm or blood, if accompanied by chest pain, or lasting longer than 3 weeks.', 'NHS Clinical Guidelines'),

(5, 5, 'Sore throats are most commonly viral in origin (such as common cold) and resolve spontaneously within 5 to 7 days.', 
 'Gargle with warm salt water (1/2 teaspoon salt in a glass of warm water) 3-4 times daily. Drink warm liquids such as herbal tea or soup broth. Rest your voice.', 
 'Seek urgent care if you experience difficulty swallowing your own saliva, difficulty breathing, or severe asymmetric throat swelling.', 'CDC Sore Throat Guidance'),

(6, 6, 'Clear nasal discharge is typically associated with allergies or the early phase of viral upper respiratory tract infections.', 
 'Rinse nasal passages gently with a sterile saline nasal spray. Drink abundant fluids to thin secretions. Elevate your head slightly while resting.', 
 'Seek evaluation if discharge turns foul-smelling from one nostril only, or lasts longer than 10 days without improvement.', 'Mayo Clinic Otolaryngology'),

(7, 7, 'Sneezing is usually triggered by airborne allergens (pollen, dust mites, pet dander) or environmental irritants.', 
 'Identify and minimize exposure to airborne irritants. Wash bed linens in warm water weekly. Keep windows closed during high pollen counts.', 
 'Seek care if sneezing is accompanied by wheezing, facial pressure pain, or difficulty breathing.', 'AAFA Allergy Guidelines'),

(8, 8, 'Nasal congestion occurs when mucosal blood vessels become engorged from inflammation. Avoid forceful blowing.', 
 'Take a warm shower and breathe in the steam. Use saline nasal mist. Keep well hydrated. Sleep with head elevated.', 
 'Seek prompt care if nasal congestion is accompanied by forehead swelling, blurred vision, or high persistent fever.', 'NHS ENT Advice'),

(9, 9, 'Skin rashes require gentle observation. Do not scratch or scrub the area to prevent secondary bacterial infection.', 
 'Keep the area clean and dry. Apply a fragrance-free gentle moisturizing lotion or pure aloe vera gel. Wear loose, soft cotton garments.', 
 'Immediately consult a doctor if the rash spreads rapidly, forms blisters, or is accompanied by fever or breathing difficulty.', 'British Association of Dermatologists'),

(10, 10, 'Pruritus (itching) can stem from dry skin, mild allergies, or environmental irritants. Avoid hot showers which strip natural skin oils.', 
 'Take lukewarm short baths. Apply a soothing unscented moisturizer immediately after bathing while skin is damp. Use cool compresses on itchy areas.', 
 'Seek medical evaluation if itching is generalized across the body, disrupts sleep consistently, or is accompanied by yellowing skin/eyes.', 'American Academy of Dermatology'),

(11, 11, 'Acne involves follicular inflammation and sebum excess. Avoid picking or squeezing lesions as this promotes scarring and bacterial spread.', 
 'Wash your face twice daily with a mild, non-comedogenic cleanser. Avoid touching your face with unwashed hands. Keep hair clean and off the forehead.', 
 'Consult a dermatologist for painful cystic bumps, nodules beneath the skin, or if over-the-counter gentle care proves ineffective.', 'AAD Clinical Guidance'),

(12, 12, 'Dry skin reflects barrier impairment and low lipid retention, common during cold dry seasons or after prolonged air conditioning.', 
 'Apply thick bland moisturizers (such as petroleum jelly or ceramide creams) twice daily. Limit shower time to under 10 minutes using lukewarm water.', 
 'Consult a dermatologist if skin cracks deeply, bleeds, or shows signs of redness, warmth, and bacterial infection.', 'Mayo Clinic Dermatology'),

(13, 13, 'Ear pain can originate from the external auditory canal, middle ear, or referred from the jaw/teeth. Never insert cotton buds or sharp objects into ear canal.', 
 NULL, -- Clinically, home remedies inside the ear canal can cause tympanic membrane rupture, so leave blank for safety.
 'Seek immediate medical attention if there is fluid or blood draining from the ear, severe dizziness, hearing loss, or swelling behind the ear.', 'ENT UK Guidelines'),

(14, 14, 'Red eyes can result from prolonged screen strain, fatigue, dry air, or mild conjunctivitis. Avoid rubbing eyes with hands.', 
 'Rest your eyes following the 20-20-20 rule (every 20 minutes look at an object 20 feet away for 20 seconds). Apply a clean, cool damp washcloth over closed eyelids.', 
 'Seek urgent ophthalmologic care if you experience deep eye pain, vision reduction, halos around lights, or severe light sensitivity.', 'American Academy of Ophthalmology'),

(15, 15, 'Excessive tearing often paradoxically arises from dry eye reflex, mild irritant exposure, or blocked tear ducts.', 
 'Avoid smoky, windy, or excessively dry environments. Wear protective sunglasses outdoors. Clean eyelid margins gently with warm water.', 
 'Consult an eye specialist if tearing is accompanied by eye pain, pus discharge, or visual distortion.', 'AAO Clinical Practice'),

(16, 16, 'Abdominal discomfort can stem from mild indigestion, gas, or dietary changes. Monitor the exact location and duration.', 
 'Sip warm water or peppermint/ginger tea. Eat small, light meals (toast, plain rice, bananas). Avoid greasy, spicy, or heavily fried meals.', 
 'SEEK EMERGENCY CARE if stomach pain is sudden and severe, the abdomen feels board-like/rigid, or if accompanied by high fever or vomiting blood.', 'ACG Digestive Guidelines'),

(17, 17, 'Nausea is an uneasy stomach sensation. Sit upright after eating and avoid rapid head or body movements.', 
 'Sip small amounts of chilled clear fluids, ginger tea, or lemon water. Eat bland foods like crackers in small portions. Get fresh airflow.', 
 'Seek medical care if nausea prevents fluid intake for over 12 hours, or if accompanied by chest pain or severe headache.', 'NHS Health Insights'),

(18, 18, 'Vomiting causes rapid fluid and electrolyte depletion. The primary initial priority is gentle, steady oral rehydration.', 
 'Wait 30-60 minutes after vomiting before sipping fluids. Take small, frequent sips (one teaspoon at a time) of Oral Rehydration Solution (ORS) or diluted electrolyte fluids.', 
 'Seek urgent care if vomiting lasts > 24 hours, if vomit contains blood or dark coffee-ground material, or if signs of severe dehydration appear.', 'WHO Diarrhoeal Disease Control'),

(19, 19, 'Diarrhea leads to rapid loss of water and essential salts (sodium, potassium). Maintaining electrolyte balance is vital.', 
 'Drink Oral Rehydration Solution (ORS) steadily after every loose stool. Consume potassium-rich bland foods like bananas, rice, and clear broths. Avoid dairy and caffeine.', 
 'Consult a physician if diarrhea contains blood or mucus, persists for more than 48 hours, or is accompanied by high fever (> 102°F).', 'CDC & WHO Diarrhea Protocol'),

(20, 20, 'Infrequent bowel movements are often linked to low dietary fiber, inadequate hydration, and sedentary lifestyle.', 
 'Gradually increase intake of dietary fiber (whole grains, oats, prunes, vegetables). Drink at least 8-10 glasses of water daily. Engage in light daily walking.', 
 'Seek medical consultation if constipation persists for weeks, is accompanied by severe abdominal cramping, or blood appears in stool.', 'World Gastroenterology Organisation'),

(21, 21, 'Indigestion (dyspepsia) involves upper digestive discomfort often triggered by eating too rapidly, large meals, or acidic foods.', 
 'Eat smaller, frequent meals and chew thoroughly. Avoid lying down for at least 2-3 hours after eating. Avoid known triggers like excessive coffee and chili.', 
 'SEEK IMMEDIATE CARE if indigestion is accompanied by chest discomfort radiating to the arm/neck, sweating, or difficulty breathing.', 'NICE Clinical Guidelines'),

(22, 22, 'Bloating is commonly caused by swallowed air, gaseous foods (beans, carbonated drinks), or sluggish digestion.', 
 'Take a brisk 15-minute walk after meals. Sip warm peppermint or fennel tea. Avoid chewing gum and drinking through straws.', 
 'Consult a gastroenterologist if bloating is progressive, painful, or accompanied by unexplained weight loss or altered bowel habits.', 'Mayo Clinic Gastroenterology'),

(23, 23, 'Joint discomfort without acute trauma can relate to strain, mild osteoarthritic changes, or repetitive activity.', 
 'Rest the affected joint. Apply an ice pack wrapped in a towel for 15-20 minutes for acute soreness, or a warm heating pad for chronic stiffness. Gentle range-of-motion stretching.', 
 'Seek medical evaluation if the joint becomes visibly red, hot, swollen, or if you are unable to bear any weight on the limb.', 'Arthritis Foundation'),

(24, 24, 'Non-specific lower back pain is frequently muscular in origin due to poor ergonomics, prolonged sitting, or heavy lifting.', 
 'Stay gently active—avoid prolonged strict bed rest. Apply heat packs for 15 minutes to relieve muscle tension. Maintain ergonomic sitting posture with lower back support.', 
 'SEEK EMERGENCY CARE if back pain is accompanied by loss of bladder/bowel control, numbness in the saddle/groin area, or progressive leg weakness.', 'NHS Back Pain Guidelines'),

(25, 25, 'Neck stiffness often stems from "tech neck", poor sleep posture, or cervical muscle strain.', 
 'Perform gentle, slow neck rolls and side-to-side stretches. Ensure your computer monitor is at eye level. Use a supportive, medium-firm ergonomic pillow.', 
 'SEEK URGENT ATTENTION if neck pain is accompanied by high fever and an inability to flex your chin to your chest (meningitis sign).', 'Mayo Clinic Musculoskeletal'),

(26, 26, 'Shoulder stiffness is often caused by muscle fatigue, rotator cuff strain, or poor overhead posture.', 
 'Rest the shoulder from repetitive overhead tasks. Apply cold compress for the first 48 hours, followed by gentle moist heat. Practice gentle pendular shoulder swings.', 
 'Seek immediate emergency care if left shoulder pain is accompanied by chest pressure, shortness of breath, or sweating.', 'American Academy of Orthopaedic Surgeons'),

(27, 27, 'Mild knee soreness frequently arises from mild patellar strain, sudden increase in physical activity, or prolonged standing.', 
 'Follow the R.I.C.E protocol (Rest, Ice for 15 mins, gentle Compression bandage, Elevation above heart level). Avoid deep squats and running on hard surfaces.', 
 'Consult an orthopedic specialist if you heard a loud "pop", cannot straighten the knee, or if severe swelling develops within 2 hours.', 'AAOS Knee Guidelines'),

(28, 28, 'Muscle cramps are sudden involuntary contractions, commonly in the calf, often due to dehydration or electrolyte imbalance.', 
 'Gently stretch the cramped muscle (pull toes upward toward shin). Massage the muscle firmly. Drink an electrolyte drink or coconut water.', 
 'Consult a physician if cramps occur daily, cause severe ongoing swelling or redness, or do not respond to hydration.', 'Mayo Clinic Sports Health'),

(29, 29, 'Mild fatigue can arise from sleep deficits, demanding work schedules, or mild nutritional shortages.', 
 'Prioritize 7-8 hours of regular nightly sleep. Stay well-hydrated throughout the day. Take short outdoor walking breaks in natural daylight.', 
 'Consult a physician if fatigue is persistent, debilitating, or accompanied by unexplained weight loss, night sweats, or swollen glands.', 'NHS Fatigue Guidance'),

(30, 30, 'Mild dizziness when standing up quickly is often benign orthostatic lightheadedness. Rise slowly from lying or seated positions.', 
 'Sit or lie down immediately if dizzy. Drink a large glass of water. Avoid sudden head turns. Rest in a well-ventilated space.', 
 'SEEK EMERGENCY ATTENTION if dizziness occurs with slurred speech, facial asymmetry, arm weakness, chest discomfort, or fainting.', 'American Heart Association'),

(31, 31, 'Mild temporary loss of appetite can accompany mild infections, stress, or digestive slowing.', 
 'Eat small, nutrient-dense meals throughout the day (soups, smoothies, fruit). Keep hydrated with lemon water or broths. Avoid forcing large meals.', 
 'Consult a general physician if poor appetite continues beyond 7 days or is accompanied by unintentional weight reduction.', 'Mayo Clinic Internal Medicine'),

(32, 32, 'Mild dehydration manifests with mild thirst, dry lips, and concentrated dark yellow urine.', 
 'Drink plain water and electrolyte solutions steadily in small amounts. Consume water-rich fruits such as watermelon, oranges, and cucumber.', 
 'Seek immediate medical attention if experiencing confusion, lack of urination for > 8 hours, dizziness, or rapid heart rate.', 'WHO Rehydration Guidelines'),

(33, 33, 'Mild environmental allergies cause nasal itching, sneezing, and watery eyes upon allergen contact.', 
 'Avoid identified allergen triggers (dust, pet dander). Use an indoor HEPA air purifier. Shower and change clothes after outdoor activities.', 
 'SEEK EMERGENCY CARE if experiencing throat tightness, tongue swelling, difficulty breathing, or dizziness (anaphylaxis warning).', 'World Allergy Organization'),

(34, 34, 'Sunburn results from ultraviolet light-induced skin damage and cellular inflammation.', 
 'Apply cold, damp compresses to affected skin. Liberally apply pure aloe vera gel or soothing calamine. Drink extra water to counteract skin dehydration.', 
 'Seek medical care for extensive blistering, high fever, severe chills, or signs of heat exhaustion.', 'Skin Cancer Foundation Guidelines'),

(35, 35, 'Minor first-degree thermal burn affects only the outer skin layer, causing redness and mild tenderness.', 
 'Immediately cool the burn under gently running cool tap water for 10-15 minutes. Never apply ice, butter, or toothpaste. Apply pure aloe vera or petroleum jelly.', 
 'Seek medical care if burn is larger than 2 inches, develops deep blisters, or involves face, hands, major joints, or genitals.', 'American Burn Association'),

(36, 36, 'Common mosquito or non-venomous insect bites cause localized histamine-mediated swelling and redness.', 
 'Wash the bite area with soap and water. Apply an ice pack wrapped in a cloth for 10 minutes to reduce swelling. Apply calamine lotion to relieve itching.', 
 'SEEK EMERGENCY CARE if you experience hives across the body, swelling around lips/eyes, or difficulty breathing.', 'CDC Vector-Borne Health'),

(37, 37, 'Motion sickness is triggered by sensory mismatch between the eyes and vestibular balance organs in inner ear.', 
 'Focus your gaze on the distant horizon. Sit in the front passenger seat of cars or over the wing on airplanes. Ensure cool, fresh air circulation. Sip ginger ale.', 
 'Consult a doctor if severe nausea prevents keeping fluids down or if motion symptoms persist long after travel ends.', 'CDC Travelers Health'),

(38, 38, 'Hiccups are diaphragm spasms usually caused by carbonated beverages, eating too fast, or sudden excitement.', 
 'Sip a glass of ice-cold water slowly. Hold your breath for 10-15 seconds. Breathe slowly into a paper bag for a brief period.', 
 'Consult a physician if hiccups persist continuously for more than 48 hours or interfere with sleeping or eating.', 'NHS Hiccup Information'),

(39, 39, 'Bad breath (halitosis) is typically caused by oral bacteria breaking down food particles on teeth and tongue.', 
 'Brush teeth twice daily for two minutes. Floss daily between all teeth. Gently scrape or brush the surface of the tongue. Drink plenty of water.', 
 'Visit a dentist if bad breath persists despite good oral hygiene, or if accompanied by bleeding gums or loose teeth.', 'American Dental Association'),

(40, 40, 'Tooth sensitivity occurs when tooth enamel thins or gums recede, exposing microscopic dentinal tubules.', 
 'Use a soft-bristled toothbrush and brush gently in small circular motions. Use a desensitizing fluoride toothpaste. Avoid acidic drinks and very cold foods.', 
 'Consult a dentist if pain is throbbing, persists after temperature stimulus is removed, or if tooth feels loose.', 'ADA Tooth Sensitivity Guide'),

(41, 41, 'Gingival bleeding during brushing indicates early gum inflammation (gingivitis) due to plaque accumulation.', 
 'Continue gentle daily brushing and flossing—do not stop oral hygiene. Rinse with warm mild salt water after meals. Schedule a professional dental cleaning.', 
 'Consult a dentist promptly if gums bleed spontaneously, look bright red and swollen, or if teeth feel loose.', 'British Dental Association'),

(42, 42, 'Aphthous ulcers (canker sores) are benign non-contagious oral lesions that usually heal in 7-10 days.', 
 'Rinse mouth gently with warm salt water. Avoid spicy, salty, or highly acidic foods that cause burning. Apply a dab of raw honey or soothing oral gel.', 
 'Consult a dentist or physician if the mouth ulcer lasts longer than 2 weeks, is unusually large, or makes eating impossible.', 'Mayo Clinic Oral Health'),

(43, 43, 'Cheilitis (chapped lips) results from weather exposure, dehydration, and repeated habit of lip licking.', 
 'Apply a thick plain lip balm containing petroleum jelly, beeswax, or shea butter frequently throughout the day. Avoid licking or peeling dry lip flakes.', 
 'Consult a dermatologist if lip fissures bleed persistently, form honey-colored crusts, or fail to heal with regular emollient use.', 'AAD Lip Care Advice'),

(44, 44, 'Dry eyes result when tear quality or quantity is insufficient, often intensified by screen use and AC environments.', 
 'Blink intentionally and frequently when viewing screens. Position screens slightly below eye level. Use preservative-free lubricating artificial tear drops.', 
 'Consult an ophthalmologist if dry eye symptoms include foreign body sensation, extreme light sensitivity, or persistent redness.', 'American Optometric Association'),

(45, 45, 'Vocal hoarseness (laryngitis) commonly follows viral respiratory infection, vocal overuse, or excessive shouting.', 
 'Rest your voice—avoid shouting, singing, and whispering (whispering actually puts more strain on vocal cords). Inhale steam and drink warm soothing fluids.', 
 'Consult an ENT specialist if hoarseness lasts more than 2 weeks, or is accompanied by difficulty swallowing or a lump in the neck.', 'American Academy of Otolaryngology'),

(46, 46, 'Mild situational anxiety or stress is a normal human response to challenging events or heavy workloads.', 
 'Practice 4-7-8 rhythmic breathing (inhale 4s, hold 7s, exhale 8s). Take a 20-minute brisk walk in nature. Limit caffeine intake. Talk with a trusted friend.', 
 'Consult a mental health professional or doctor if anxiety becomes overwhelming, causes panic attacks, or interferes with work/life.', 'NIMH Mental Health Resources'),

(47, 47, 'Occasional sleeplessness is frequently connected to irregular schedules, screen light exposure before bed, or stress.', 
 'Maintain a fixed sleep and wake time every day. Turn off smartphones, computers, and TVs 60 minutes before bed. Keep bedroom cool, quiet, and dark.', 
 'Consult a physician if insomnia continues for several weeks or causes severe daytime fatigue and impairment.', 'Sleep Foundation Guidelines'),

(48, 48, 'Mild evening ankle swelling can occur after long periods of standing, walking, or hot weather.', 
 'Elevate legs on pillows above heart level for 20-30 minutes when resting. Avoid sitting with crossed legs. Avoid excessive sodium in food.', 
 'SEEK IMMEDIATE EMERGENCY CARE if swelling is sudden, affects only one leg with calf warmth/pain, or is accompanied by shortness of breath.', 'American Heart Association'),

(49, 49, 'Primary menstrual cramping is caused by prostaglandin-mediated uterine muscle contractions during menstruation.', 
 'Apply a warm heating pad to lower abdomen. Take a warm bath. Engage in gentle walking or yoga stretches. Sip warm ginger or chamomile tea.', 
 'Consult a gynecologist if menstrual cramps are progressively severe, unresponsive to simple heat/analgesics, or disrupt schooling/work.', 'ACOG Women Health Guidance'),

(50, 50, 'Cold hands commonly occur in cold weather or during states of nervous stress due to peripheral blood vessel constriction.', 
 'Wear warm mittens or gloves in cool environments. Run hands under lukewarm water. Avoid smoking and limit caffeine which constrict blood vessels.', 
 'Consult a physician if fingers change color dramatically (white to blue to red with throbbing pain - Raynaud), or develop skin sores.', 'Mayo Clinic Vascular Care')
ON DUPLICATE KEY UPDATE `preliminary_guidance`=VALUES(`preliminary_guidance`);

-- 5. Insert Predefined Chatbot FAQs
INSERT INTO `chatbot_faqs` (`id`, `category`, `keywords`, `question`, `answer`) VALUES
(1, 'General', 'how works, platform, what is ayucare, overview', 'How does AyuCare work?', 'AyuCare (आयुCare) is an educational healthcare guidance platform. You can enter or select your symptoms, and our system analyzes them against clinically curated guidance to provide preliminary care advice, safe home-care tips for mild conditions, and recommendations for appropriate medical specialists.'),
(2, 'Symptom Checker', 'check symptoms, symptom checker, how to check, form', 'How do I check my symptoms?', 'Click on "Check Your Symptoms" in the navigation bar or home page. Select your primary symptom from our comprehensive 50-symptom list, specify its duration and severity (Mild, Moderate, or Severe), describe how you feel, and click "Submit Symptoms" to get an instant guidance report.'),
(3, 'Specialists', 'which specialist, doctor recommendation, who to see', 'Which specialist should I consult?', 'AyuCare automatically recommends an appropriate specialist category based on your reported symptoms (e.g., Dermatologist for skin rashes, ENT Specialist for ear/throat pain, Neurologist for persistent migraines). You can explore doctors and request consultations on our "Find a Specialist" page.'),
(4, 'Symptom Checker', 'what information, details, enter, duration, severity', 'What information should I enter in the Symptom Checker?', 'Please provide: 1) Your primary symptom, 2) Duration (e.g., 2 days, 1 week), 3) Severity level (Mild, Moderate, or Severe), and 4) A brief description of how you feel, including any other sensations. This helps generate the most accurate preliminary guidance.'),
(5, 'Consultation', 'request consultation, book appointment, see doctor', 'How can I request a consultation?', 'Go to the "Find a Specialist" page or use the recommendation card from your Symptom Checker report. Choose a specialist or registered doctor, select your preferred date and time, add a brief note, and submit your request. You can track its status in your Patient Dashboard.'),
(6, 'Safety & Limitations', 'diagnosis, cure, medicine, prescription, diagnosis tool', 'Is AyuCare a medical diagnosis tool?', 'No. AyuCare is strictly an educational prototype designed for preliminary guidance and healthcare navigation. It does NOT provide formal medical diagnoses, nor does it prescribe prescription drugs. Always consult a qualified healthcare professional for medical concerns.'),
(7, 'Emergency', 'emergency, chest pain, stroke, dying, severe breath, urgent', 'What should I do in a medical emergency?', 'If you or someone around you is experiencing severe symptoms—such as crushing chest pain, difficulty breathing, slurred speech, sudden numbness, high fever with stiff neck, or heavy bleeding—immediately call your local emergency medical service (112 / 108 / 911) or visit the nearest hospital emergency department.'),
(8, 'Accounts', 'register, login, signup, patient account, doctor account', 'How do I create an account or sign in?', 'Click on "Register" in the top navigation bar to create a Patient account, or visit the Doctor Portal link to register as a healthcare provider. After registration, log in using your registered email and password to access your personalized dashboard and history.'),
(9, 'Privacy', 'privacy, data safe, secure, medical records', 'Is my health data secure on AyuCare?', 'Yes. AyuCare uses secure session/token-based authentication and hashed passwords. Your private health history is accessible only by you. Doctors can only view consultation details that you explicitly request with them.'),
(10, 'Home Care', 'home remedies, home care, natural care, mild', 'Can I rely solely on home-care tips?', 'Home-care tips on AyuCare are provided only for mild, self-limiting discomfort (such as drinking fluids or resting). They are NOT cures and should never replace professional medical attention, especially if symptoms worsen or do not improve.')
ON DUPLICATE KEY UPDATE `question`=VALUES(`question`);
