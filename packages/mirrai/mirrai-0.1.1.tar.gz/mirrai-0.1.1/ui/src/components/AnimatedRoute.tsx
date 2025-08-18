import { motion, Transition } from "framer-motion";
import { ReactNode } from "react";

interface AnimatedRouteProps {
    children: ReactNode;
}

const pageVariants = {
    initial: {
        opacity: 0,
    },
    in: {
        opacity: 1,
    },
    out: {
        opacity: 0,
    },
};

const pageTransition: Transition = {
    type: "tween",
    ease: "easeInOut",
    duration: 0.2,
};

export function AnimatedRoute({ children }: AnimatedRouteProps) {
    return (
        <motion.div
            initial="initial"
            animate="in"
            exit="out"
            variants={pageVariants}
            transition={pageTransition}
            style={{ height: "100%" }}
        >
            {children}
        </motion.div>
    );
}
