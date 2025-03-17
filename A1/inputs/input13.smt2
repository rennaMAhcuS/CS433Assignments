(set-logic AUFLIA)
(assert (=> 
            (exists ((w Int)) 
                (forall ((x Int)) 
                    (exists ((y Int)) 
                        (forall ((z Int)) (> (+ w x) y))))) 

            (exists ((v Int)) (< v 10))))
(check-sat)


