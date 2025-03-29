(set-logic AUFLIA)
(assert (forall ((w Int)) 
            (exists ((x Int)) 
                (forall ((y Int)) 
                    (exists ((z Int)) 
                        (and (> (+ w x) y) (< (* y z) w)))))))
(check-sat)

