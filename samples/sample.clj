;; Recursive factorial calculation
(defn factorial [n]
  (if (<= n 1)
    1
    (* n (factorial (dec n)))))

;; Data pipeline: map, filter, reduce
(defn process-data [coll]
  (->> coll
       (map #(* % 2))
       (filter even?)
       (reduce +)))
