-- ========================================================
-- SCRIPT SQL DE CORRECTION DES PHARMACIES DE LIBREVILLE
-- ========================================================
-- Exécutez ce script sur votre base de données VPS
-- pour corriger automatiquement les pharmacies corrompues

-- 1. Voir les pharmacies problématiques avant correction
SELECT 
    id,
    code,
    nom,
    latitude,
    longitude,
    type_etablissement,
    CASE 
        WHEN code IS NULL OR code = '' THEN 'CODE MANQUANT'
        WHEN nom IS NULL OR nom = '' THEN 'NOM MANQUANT'
        WHEN latitude IS NULL OR longitude IS NULL THEN 'GPS MANQUANT'
        WHEN latitude < -90 OR latitude > 90 THEN 'LATITUDE INVALIDE'
        WHEN longitude < -180 OR longitude > 180 THEN 'LONGITUDE INVALIDE'
        ELSE 'OK'
    END as probleme
FROM pharmacy 
WHERE ville = 'Libreville'
ORDER BY id;

-- 2. Supprimer les pharmacies avec données critiques manquantes
DELETE FROM pharmacy 
WHERE ville = 'Libreville' AND (
    code IS NULL OR code = '' OR
    nom IS NULL OR nom = ''
);

-- 3. Corriger les coordonnées GPS invalides ou manquantes
UPDATE pharmacy 
SET 
    latitude = 0.4162,
    longitude = 9.4673
WHERE ville = 'Libreville' AND (
    latitude IS NULL OR longitude IS NULL OR
    latitude < -90 OR latitude > 90 OR 
    longitude < -180 OR longitude > 180
);

-- 4. Corriger les types d'établissement invalides
UPDATE pharmacy 
SET type_etablissement = 'pharmacie_generale'
WHERE ville = 'Libreville' AND (
    type_etablissement NOT IN ('pharmacie_generale', 'depot_pharmaceutique', 'pharmacie_hospitaliere')
    OR type_etablissement IS NULL
);

-- 5. Corriger les dates de garde invalides (start_date > end_date)
UPDATE pharmacy 
SET 
    is_garde = FALSE,
    garde_start_date = NULL,
    garde_end_date = NULL
WHERE ville = 'Libreville' AND (
    garde_start_date > garde_end_date
);

-- 6. Vérifier le résultat final
SELECT 
    id,
    code,
    nom,
    latitude,
    longitude,
    type_etablissement,
    is_garde,
    'OK' as status
FROM pharmacy 
WHERE ville = 'Libreville'
ORDER BY id;

-- ========================================================
-- FIN DU SCRIPT
-- ========================================================
-- Après correction, redémarrez votre application Flask
-- et vérifiez que les pharmacies s'affichent correctement
