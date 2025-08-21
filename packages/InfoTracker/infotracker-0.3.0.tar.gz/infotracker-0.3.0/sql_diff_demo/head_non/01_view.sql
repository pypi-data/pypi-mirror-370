CREATE VIEW WarehouseDB.dbo._diff_demo AS
SELECT
  CAST(o.OrderID AS INT)              AS id,
  CAST(o.TotalAmount AS DECIMAL(10,2)) AS amount,
  CAST(NULL AS INT)                     AS optional_flag  -- nowa nullable
FROM STG.dbo.Orders AS o;
GO
