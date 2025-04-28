-- Calculate sum, average and max from table
function calculate_stats(numbers)
  local sum = 0
  local max = -math.huge
  for _, num in ipairs(numbers) do
    sum = sum + num
    if num > max then max = num end
  end
  return {sum = sum, average = sum/#numbers, max = max}
end
