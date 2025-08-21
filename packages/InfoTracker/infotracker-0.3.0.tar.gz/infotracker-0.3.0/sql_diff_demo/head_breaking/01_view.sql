CREATE VIEW WarehouseDB.dbo._diff_demo AS
SELECT
  CAST(o.OrderID AS INT)                AS id,
  CAST(o.TotalAmount AS NVARCHAR(50))   AS amount   -- typ zmieniony
FROM STG.dbo.Orders AS o;
GO
