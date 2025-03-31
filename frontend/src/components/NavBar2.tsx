import React from "react";
import { Box, Flex, HStack, Link, Text } from "@chakra-ui/react";
import { Link as ScrollLink } from "react-scroll";

function NavBar() {
  return (
    <Box h="50px">
      <HStack h={16} alignItems="center" w="90%" ml="2%">
        <Flex>
          <ScrollLink to="home" smooth={true} duration={500} offset={-40}>
            <Link px={2} py={1} rounded="md" color="white">
              Home
            </Link>
          </ScrollLink>
        </Flex>
        {/* <Flex>
          <ScrollLink to="experience" smooth={true} duration={500} offset={40}>
            <Link px={2} py={1} rounded="md" color="white">
              Experience
            </Link>
          </ScrollLink>
        </Flex> */}
      </HStack>
    </Box>
  );
}
export default NavBar;
