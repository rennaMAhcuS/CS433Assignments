(set-logic AUFLIA)
(assert (not 
            (exists ((x Int)) 
                (forall ((y Int)) 
                    (exists ((z Int)) (= (+ x y) z))))))
(check-sat)

