(set-logic AUFLIA)
(assert (forall ((x Int)) (exists ((y Int)) (forall ((z Int)) (> (+ x y) z)))))
(check-sat)

