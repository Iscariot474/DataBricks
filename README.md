# DataBricks SQL experience for measuring 4L of water with 2 bukcets one with 5L capacity and other with 3L capacity

-- Possible Tables
CREATE TABLE Buckets (
    step INT PRIMARY KEY,
    action VARCHAR(50),
    bucket5 INT,
    bucket3 INT
);

-- method 
INSERT INTO Bucket VALUES
(1, 'Fill 5L'          ,                 5, 0),
(2, 'Transfer 5L to 3L',                 2, 3),
(3, 'Empty  3L'        ,                 2, 0),
(4, 'Transfer 2L to 3L',                 0, 2),
(5, 'Fill 5L'          ,                 5, 2),
(6, 'Transfer 5L to 3L',                 4, 3);

-- consult final solution (4 l on the bucket of 5L)
SELECT *
FROM Buckets
WHERE bucket5 = 4;
