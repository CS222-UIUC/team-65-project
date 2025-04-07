import { Flex, Link } from "@chakra-ui/react";
import { Link as ScrollLink } from "react-scroll";

const Navbar = () => {
  return (
    <Flex
      as="nav"
      position="fixed"
      top={0}
      width="100%"
      bg="rgba(0, 0, 0, 0.8)"
      backdropFilter="blur(10px)"
      color="white"
      py={3}
      px={5}
      justifyContent="center"
      alignItems="center"
      boxShadow="md"
    >
      <ScrollLink to="home" smooth={true} duration={500} offset={-40}>
        <Link
          px={4}
          py={2}
          rounded="md"
          _hover={{ bg: "whiteAlpha.300", transition: "0.3s" }}
        >
          Home
        </Link>
      </ScrollLink>
    </Flex>
  );
};

export default Navbar;