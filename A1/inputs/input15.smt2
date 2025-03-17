(set-logic AUFLIA)
(assert (=> 
            (not 
                (xor 
                    (forall ((p Int)) 
                        (exists ((q Int)) 

                            (forall ((r Int)) 
                                (exists ((s Int)) 
                                    (forall ((t Int)) (> (+ p q r) (* s t))))))) 
                    (exists ((u Int)) (< u 0)))) 
            (forall ((v Int)) (exists ((w Int)) (= v w)))))
(check-sat)

