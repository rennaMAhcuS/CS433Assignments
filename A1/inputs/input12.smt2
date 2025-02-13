(set-logic AUFLIA)
(assert (xor 
            (forall ((a Int)) 
                (exists ((b Int)) 
                    (forall ((c Int)) (> (+ a b) c)))) 
            (exists ((d Int)) (< d 0))))
(check-sat)

