CREATE VIEW WarehouseDB.dbo._diff_demo AS
SELECT
  CAST(o.OrderID AS INT)              AS id,
  CAST(o.TotalAmount AS DECIMAL(10,2)) AS amount
FROM STG.dbo.Orders AS o;
GO
