-- ============================================================
-- AIRBNB DATA ANALYSIS — SQL QUERIES
-- Database: airbnb_project
-- Table: cleaned_airbnb_data
-- ============================================================


-- ────────────────────────────────────────────────────────────
-- QUERY 1: Market Penetration
-- Global vs local popularity ranking for every listing
-- Business Question: Is this listing popular platform-wide
-- or just dominant in its local neighbourhood?
-- ────────────────────────────────────────────────────────────
SELECT 
    Name,
    neighbourhood,
    `room type`,
    `number of reviews`,
    RANK() OVER (
        ORDER BY `number of reviews` DESC
    ) AS global_popularity_rank,
    DENSE_RANK() OVER (
        PARTITION BY neighbourhood 
        ORDER BY `number of reviews` DESC
    ) AS neighbourhood_popularity_rank
FROM cleaned_airbnb_data
WHERE Name IS NOT NULL
ORDER BY global_popularity_rank ASC
LIMIT 20;


-- ────────────────────────────────────────────────────────────
-- QUERY 2: Trust Index
-- Verified host ratio per neighbourhood and room type
-- Business Question: What % of listings in each neighbourhood
-- are from verified hosts?
-- ────────────────────────────────────────────────────────────
WITH VerificationCounts AS (
    SELECT 
        neighbourhood,
        `room type`,
        Name,
        host_identity_verified,
        COUNT(*) OVER (
            PARTITION BY neighbourhood
        ) AS total_listings_in_neighbourhood,
        SUM(CASE WHEN host_identity_verified = 'VERIFIED' THEN 1 ELSE 0 END) OVER (
            PARTITION BY neighbourhood
        ) AS verified_listings_in_neighbourhood
    FROM cleaned_airbnb_data
)
SELECT 
    neighbourhood,
    `room type`,
    Name,
    host_identity_verified,
    total_listings_in_neighbourhood,
    ROUND(
        (verified_listings_in_neighbourhood / total_listings_in_neighbourhood) * 100, 2
    ) AS neighbourhood_trust_percentage
FROM VerificationCounts
ORDER BY total_listings_in_neighbourhood DESC, Name;


-- ────────────────────────────────────────────────────────────
-- QUERY 3: Room Type Premium
-- Price variance from room type average
-- Business Question: Is this listing priced above or below
-- the average for its room type?
-- ────────────────────────────────────────────────────────────
SELECT 
    Name,
    `room type`,
    price,
    AVG(price) OVER (
        PARTITION BY `room type`
    ) AS average_price_for_room_type,
    price - AVG(price) OVER (
        PARTITION BY `room type`
    ) AS price_variance_from_avg,
    ROUND(
        PERCENT_RANK() OVER (
            PARTITION BY `room type` 
            ORDER BY price ASC
        ) * 100, 2
    ) AS price_percentile_in_room_type
FROM cleaned_airbnb_data
WHERE Name IS NOT NULL
ORDER BY `room type`, price DESC;


-- ────────────────────────────────────────────────────────────
-- QUERY 4: Neighbourhood Standouts
-- Top 3 most reviewed verified listings per neighbourhood
-- Business Question: Who are the top 3 verified hosts
-- in every neighbourhood?
-- ────────────────────────────────────────────────────────────
WITH RankedNeighbourhoodHotels AS (
    SELECT 
        neighbourhood,
        Name,
        `number of reviews`,
        DENSE_RANK() OVER (
            PARTITION BY neighbourhood 
            ORDER BY `number of reviews` DESC
        ) AS local_rank
    FROM cleaned_airbnb_data
    WHERE host_identity_verified = 'VERIFIED' 
    AND Name IS NOT NULL
)
SELECT 
    neighbourhood, 
    local_rank, 
    Name, 
    `number of reviews`
FROM RankedNeighbourhoodHotels
WHERE local_rank <= 3
ORDER BY neighbourhood, local_rank;


-- ────────────────────────────────────────────────────────────
-- QUERY 5: Value Score
-- Low fee, high demand listings
-- Business Question: Which verified listings charge
-- below-average fees but still attract high review counts?
-- ────────────────────────────────────────────────────────────
WITH FeeAnalysis AS (
    SELECT 
        Name,
        neighbourhood,
        price,
        CAST(REPLACE(`service fee`, '$', '') AS DECIMAL) AS clean_service_fee,
        `number of reviews`,
        AVG(
            CAST(REPLACE(`service fee`, '$', '') AS DECIMAL)
        ) OVER (PARTITION BY neighbourhood) AS avg_neighbourhood_fee
    FROM cleaned_airbnb_data
    WHERE host_identity_verified = 'VERIFIED' 
    AND Name IS NOT NULL
)
SELECT 
    Name, 
    neighbourhood, 
    price, 
    clean_service_fee,
    avg_neighbourhood_fee,
    clean_service_fee - avg_neighbourhood_fee AS fee_deviation,
    `number of reviews`,
    ROUND(
        CUME_DIST() OVER (ORDER BY `number of reviews` DESC) * 100, 2
    ) AS popularity_top_percentile
FROM FeeAnalysis
WHERE clean_service_fee < 150
ORDER BY `number of reviews` DESC
LIMIT 20;
