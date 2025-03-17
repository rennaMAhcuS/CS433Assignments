(set-logic AUFLIA)
(assert (=> 
            (forall ((x Int)) (exists ((y Int)) (> x y))) 
            (exists ((z Int)) (< z 0))))
(check-sat)

